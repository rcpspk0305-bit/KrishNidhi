/** @type {import('next').NextConfig} */
const nextConfig = {
  // Keep isolated browser fixtures from sharing generated files with the app.
  distDir: process.env.NEXT_BUILD_DIR || ".next",
};

export default nextConfig;
