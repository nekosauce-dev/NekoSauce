/** @type {import('next').NextConfig} */
const nextConfig = {
    reactStrictMode: true,
    env: {
        FOOTER_DISCORD_LINK:
            process.env.FRONTEND_FOOTER_DISCORD_LINK &&
            process.env.FRONTEND_FOOTER_DISCORD_LINK.length > 0
                ? process.env.FRONTEND_FOOTER_DISCORD_LINK
                : undefined,
        FOOTER_TWITTER_LINK:
            process.env.FRONTEND_FOOTER_TWITTER_LINK &&
            process.env.FRONTEND_FOOTER_TWITTER_LINK.length > 0
                ? process.env.FRONTEND_FOOTER_TWITTER_LINK
                : undefined,
        FOOTER_REDDIT_LINK:
            process.env.FRONTEND_FOOTER_REDDIT_LINK &&
            process.env.FRONTEND_FOOTER_REDDIT_LINK.length > 0
                ? process.env.FRONTEND_FOOTER_REDDIT_LINK
                : undefined,
        FOOTER_DONATE_LINK:
            process.env.FRONTEND_FOOTER_DONATE_LINK &&
            process.env.FRONTEND_FOOTER_DONATE_LINK.length > 0
                ? process.env.FRONTEND_FOOTER_DONATE_LINK
                : undefined,
        FUNDING_PROGRESS: process.env.FRONTEND_FUNDING_PROGRESS
            ? process.env.FRONTEND_FUNDING_PROGRESS
            : undefined,
        FUNDING_PROGRESS_FORMAT: process.env.FRONTEND_FUNDING_PROGRESS_FORMAT
            ? process.env.FRONTEND_FUNDING_PROGRESS_FORMAT
            : "{value}%",
    },
};

module.exports = nextConfig;
