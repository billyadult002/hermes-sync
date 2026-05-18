import { useCallback, useEffect, useRef, useState } from 'react'
import { Box, Button, Flex, Text, Textarea } from '@chakra-ui/react'
import api from '../services/api'
import { t } from '../i18n'
import { theme } from '../styles/theme'
import { PageTitle, Panel } from '../components/PageShell'

const POLL_INTERVAL_MS = 2000
const POLL_TIMEOUT_MS = 240000

function stepLabel(task) {
  const steps = Array.isArray(task?.steps) ? task.steps : []
  const current =
    steps.find((s) => s?.status === 'running') ||
    steps.find((s) => s?.status === 'pending') ||
    steps[steps.length - 1] ||
    {}
  return current?.name || current?.type || ''
}

function failureText(task) {
  const result = task?.result || {}
  const attempts = Array.isArray(result?.trace?.provider_attempts)
    ? result.trace.provider_attempts.slice(-6)
    : []
  const traceLines = attempts
    .map((a) => {
      const p = a?.provider || 'provider'
      const m = a?.model ? `/${a.model}` : ''
      const s = a?.status || 'failed'
      const e = a?.error ? `: ${a.error}` : ''
      return `  ${p}${m} ${s}${e}`
    })
    .join('\n')
  const err = task?.error || result?.error || 'legal workflow failed'
  return `${err}${traceLines ? `\n\nRuntime trace:\n${traceLines}` : ''}`
}

export default function Legal() {
  const [query, setQuery] = useState('')
  const [status, setStatus] = useState('idle') // idle | submitting | polling | done | error
  const [stepInfo, setStepInfo] = useState('')
  const [result, setResult] = useState(null)
  const [errorMsg, setErrorMsg] = useState('')
  const pollTimer = useRef(null)
  const deadlineRef = useRef(0)
  const taskIdRef = useRef(null)
  const pollRef = useRef(null)

  const stopPolling = useCallback(() => {
    if (pollTimer.current) {
      clearTimeout(pollTimer.current)
      pollTimer.current = null
    }
  }, [])

  const poll = useCallback(async () => {
    if (!taskIdRef.current) return
    try {
      const res = await api.get(`/api/runtime/task/${encodeURIComponent(taskIdRef.current)}`)
      const task = res.data || {}
      const label = stepLabel(task)
      if (label) setStepInfo(label)

      if (task.status === 'done') {
        stopPolling()
        setResult(task.result || task)
        setStatus('done')
        return
      }
      if (task.status === 'failed') {
        stopPolling()
        setErrorMsg(failureText(task))
        setStatus('error')
        return
      }
    } catch {
      if (Date.now() >= deadlineRef.current) {
        stopPolling()
        setErrorMsg(t('legalTimeout'))
        setStatus('error')
        return
      }
    }
    if (Date.now() >= deadlineRef.current) {
      stopPolling()
      setErrorMsg(t('legalTimeout'))
      setStatus('error')
      return
    }
    pollTimer.current = setTimeout(() => pollRef.current?.(), POLL_INTERVAL_MS)
  }, [stopPolling])

  useEffect(() => {
    pollRef.current = poll
  }, [poll])

  const submit = useCallback(async () => {
    const text = query.trim()
    if (!text) return
    stopPolling()
    setStatus('submitting')
    setResult(null)
    setErrorMsg('')
    setStepInfo('')
    taskIdRef.current = null

    try {
      const res = await api.post('/api/orchestrate', {
        skill: 'trade-finance-instruments#legal',
        task: text,
        prompt: text,
        skip_memory: true,
        max_iter: 1,
      })
      const payload = res.data || {}
      if (!payload.task_id) {
        setErrorMsg(payload.error || payload.message || t('legalStartFailed'))
        setStatus('error')
        return
      }
      taskIdRef.current = payload.task_id
      deadlineRef.current = Date.now() + POLL_TIMEOUT_MS
      setStatus('polling')
      pollTimer.current = setTimeout(() => pollRef.current?.(), POLL_INTERVAL_MS)
    } catch (err) {
      setErrorMsg(err?.response?.data?.error || err.message || t('legalStartFailed'))
      setStatus('error')
    }
  }, [query, stopPolling])

  const reset = useCallback(() => {
    stopPolling()
    setStatus('idle')
    setResult(null)
    setErrorMsg('')
    setStepInfo('')
    taskIdRef.current = null
  }, [stopPolling])

  const isRunning = status === 'submitting' || status === 'polling'

  return (
    <Box>
      <PageTitle>{t('legal')}</PageTitle>

      <Panel mb="20px">
        <Text fontSize="13px" color={theme.subtext} mb="10px">
          {t('legalCaption')}
        </Text>
        <Textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={t('legalPlaceholder')}
          rows={5}
          mb="12px"
          bg={theme.background}
          borderColor={theme.border}
          color={theme.text}
          fontSize="14px"
          _focus={{ borderColor: theme.secondary }}
          disabled={isRunning}
        />
        <Flex gap="10px">
          <Button
            onClick={submit}
            disabled={!query.trim() || isRunning}
            bg={theme.secondary}
            color="white"
            size="sm"
            _hover={{ opacity: 0.85 }}
          >
            {isRunning ? t('legalRunning') : t('legalSubmit')}
          </Button>
          {(status !== 'idle') && (
            <Button onClick={reset} variant="outline" size="sm" borderColor={theme.border} color={theme.subtext}>
              {t('legalReset')}
            </Button>
          )}
        </Flex>
      </Panel>

      {isRunning && (
        <Panel mb="20px">
          <Text fontSize="13px" color={theme.subtext}>
            {t('legalPolling')}
            {stepInfo ? ` · ${stepInfo}` : ''}
          </Text>
        </Panel>
      )}

      {status === 'error' && (
        <Panel mb="20px" borderColor="red.300">
          <Text fontSize="13px" fontWeight="700" color="red.400" mb="6px">
            {t('legalError')}
          </Text>
          <Text fontSize="13px" color={theme.text} whiteSpace="pre-wrap">
            {errorMsg}
          </Text>
        </Panel>
      )}

      {status === 'done' && result && (
        <Panel>
          {result.final_output && (
            <Box mb="16px">
              <Text fontSize="12px" color={theme.subtext} fontWeight="700" mb="4px" textTransform="uppercase">
                {t('legalOutput')}
              </Text>
              <Text fontSize="14px" color={theme.text} whiteSpace="pre-wrap">
                {result.final_output}
              </Text>
            </Box>
          )}
          {result.decision && (
            <Box mb="16px">
              <Text fontSize="12px" color={theme.subtext} fontWeight="700" mb="4px" textTransform="uppercase">
                {t('legalDecision')}
              </Text>
              <Text fontSize="14px" color={theme.text}>
                {typeof result.decision === 'object'
                  ? JSON.stringify(result.decision, null, 2)
                  : String(result.decision)}
              </Text>
            </Box>
          )}
          {result.artifact && (
            <Box mb="16px">
              <Text fontSize="12px" color={theme.subtext} fontWeight="700" mb="4px" textTransform="uppercase">
                {t('legalArtifact')}
              </Text>
              <Text fontSize="14px" color={theme.text} whiteSpace="pre-wrap">
                {typeof result.artifact === 'string' ? result.artifact : JSON.stringify(result.artifact, null, 2)}
              </Text>
            </Box>
          )}
        </Panel>
      )}
    </Box>
  )
}
