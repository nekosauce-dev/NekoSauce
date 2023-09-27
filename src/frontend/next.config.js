/** @type {import('next').NextConfig} */
const nextConfig = {
    reactStrictMode: true,
    env: {
        FOOTER_DISCORD_LINK: process.env.FRONTEND_FOOTER_DISCORD_LINK,
        FOOTER_TWITTER_LINK: process.env.FRONTEND_FOOTER_TWITTER_LINK,
        FOOTER_REDDIT_LINK: process.env.FRONTEND_FOOTER_REDDIT_LINK,
        FOOTER_DONATE_LINK: process.env.FRONTEND_FOOTER_DONATE_LINK,
        FUNDING_PROGRESS: process.env.FRONTEND_FUNDING_PROGRESS,
        FUNDING_PROGRESS_FORMAT: process.env.FRONTEND_FUNDING_PROGRESS_FORMAT
            ? process.env.FRONTEND_FUNDING_PROGRESS_FORMAT
            : "{value}%",
    },
};

module.exports = nextConfig;
