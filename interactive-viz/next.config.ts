import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  output: "export",
  basePath: "/choptuik_ac_bc",
  images: {
    unoptimized: true,
  },
  trailingSlash: true,
};

export default nextConfig;
