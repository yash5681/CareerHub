const localtunnel = require('localtunnel');

async function startTunnel() {
  try {
    const tunnel = await localtunnel({ port: 8000, subdomain: 'careerhub-yash' });
    console.log(`LOCALTUNNEL_URL: ${tunnel.url}`);

    tunnel.on('close', () => {
      console.log('Tunnel closed. Reconnecting in 3s...');
      setTimeout(startTunnel, 3000);
    });

    tunnel.on('error', (err) => {
      console.error('Tunnel error:', err.message);
      tunnel.close();
    });
  } catch (err) {
    console.error('Tunnel connection failed:', err.message);
    setTimeout(startTunnel, 5000);
  }
}

startTunnel();
