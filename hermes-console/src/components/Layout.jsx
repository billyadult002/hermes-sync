import { Box, Flex, HStack, Text, VStack } from '@chakra-ui/react'
import { NavLink } from 'react-router-dom'
import { t } from '../i18n'
import { theme } from '../styles/theme'
import ControlPanelMini from './ControlPanelMini'
import LanguageSwitcher from './LanguageSwitcher'

const navItems = [
  { to: '/', labelKey: 'chat' },
  { to: '/dashboard', labelKey: 'dashboard' },
  { to: '/legal', labelKey: 'legal' },
  { to: '/workspace/google-workspace', labelKey: 'workspace' },
  { to: '/control', labelKey: 'control' },
]

export default function Layout({ children }) {
  return (
    <Flex minH="100vh" bg={theme.background} fontFamily={theme.font.family} color={theme.text}>
      <Box
        as="aside"
        w={{ base: '76px', md: '248px' }}
        bg={theme.primary}
        color="white"
        borderRight={`1px solid ${theme.primary}`}
        p={{ base: '14px', md: '20px' }}
      >
        <HStack gap="10px" mb="28px">
          <Box w="32px" h="32px" borderRadius={`${theme.radius}px`} bg={theme.secondary} />
          <Box display={{ base: 'none', md: 'block' }}>
            <Text fontWeight="850" fontSize="17px">
              {theme.copilot.label}
            </Text>
            <Text color="#9ca3af" fontSize="12px">
              {t('console')}
            </Text>
          </Box>
        </HStack>
        <VStack align="stretch" gap="6px">
          {navItems.map((item) => {
            const label = t(item.labelKey)
            return (
              <NavLink key={item.to} to={item.to} end={item.to === '/'}>
                {({ isActive }) => (
                  <Box
                    px="12px"
                    py="10px"
                    borderRadius={`${theme.radius}px`}
                    bg={isActive ? theme.secondary : 'transparent'}
                    color={isActive ? '#ffffff' : '#c7d0df'}
                    fontSize="14px"
                    fontWeight="750"
                  >
                    <Text display={{ base: 'none', md: 'block' }}>{label}</Text>
                    <Text display={{ base: 'block', md: 'none' }}>{label.slice(0, 1)}</Text>
                  </Box>
                )}
              </NavLink>
            )
          })}
        </VStack>
      </Box>
      <Box flex="1" minW="0">
        <Flex
          as="header"
          h="64px"
          align="center"
          justify="space-between"
          px={{ base: '18px', md: '28px' }}
          borderBottom={`1px solid ${theme.border}`}
          bg={theme.panel}
        >
          <Box>
            <Text color={theme.text} fontWeight="850">
              {theme.copilot.label}
            </Text>
            <Text color={theme.subtext} fontSize="12px">
              Powered by Hermes Runtime
            </Text>
          </Box>
          <Box display={{ base: 'none', xl: 'block' }}>
            <ControlPanelMini />
          </Box>
          <LanguageSwitcher />
          <Box className="liveIndicator">{t('live')}</Box>
        </Flex>
        <Box as="main" p={{ base: '18px', md: '20px' }}>
          <Box maxW="1100px" mx="auto" w="100%">
            {children}
          </Box>
        </Box>
      </Box>
    </Flex>
  )
}
