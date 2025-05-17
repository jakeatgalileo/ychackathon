/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*' // Assuming the backend runs on port 8000
      }
    ]
  }
};

module.exports = nextConfig; 