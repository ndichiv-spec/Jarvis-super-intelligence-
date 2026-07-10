/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "standalone",
  poweredByHeader: false,
  reactStrictMode: true,
  experimental: {
    optimizePackageImports: ["lucide-react", "recharts", "framer-motion", "@xyflow/react"],
  },
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${process.env.NEXT_PUBLIC_GATEWAY_URL || "http://localhost:8000"}/gateway/:path*`,
      },
      {
        source: "/api/ws/:path*",
        destination: `${process.env.NEXT_PUBLIC_GATEWAY_WS_URL || "ws://localhost:8000"}/gateway/ws/:path*`,
      },
    ];
  },
};

export default nextConfig;
