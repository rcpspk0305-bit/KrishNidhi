/** @type {import('next').NextConfig} */
const nextConfig = {
  // Keep isolated browser fixtures from sharing generated files with the app.
  distDir: process.env.NEXT_BUILD_DIR || ".next",
  async rewrites() {
    const backend = (process.env.BACKEND_URL || "http://127.0.0.1:8000").replace(/\/$/, "");
    return [{ source: "/backend/:path*", destination: `${backend}/:path*` }];
  },
};

export default nextConfig;
