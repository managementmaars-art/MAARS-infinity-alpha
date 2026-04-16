module.exports = {
  apps: [
    {
      name: 'mission-control-server',
      script: 'server/index.js',
      cwd: '/root/.openclaw/workspace/agents/tank/mission-control',
      env: {
        NODE_ENV: 'production',
        PORT: 3000,
        MC_AUTH_USER: 'architect',
        MC_AUTH_PASS: 'ZionMatrix2026!',
        MC_AGENT_TOKEN: '74dc90b4c3bad295730b450f268bccfc9bc5d0c1a5afb04da929be53f3ed6221',
        OPENCLAW_GATEWAY_TOKEN: '4cba3d164fd31935cea1ad0c98a795983c3cd30ad880f42c478f34583395c44f'
      }
    }
  ]
};
