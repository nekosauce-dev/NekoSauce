import "./globals.css";
import localFont from "next/font/local";
import { Nunito_Sans, Inter } from "next/font/google";

const Caturday = localFont({
    src: "Caturday.ttf",
    variable: "--font-caturday",
    display: "swap",
});


export const metadata = {
    title: "NekoSauce - Anime, Manga and Art Sauce Finder",
    description:
        "Find your favorite anime, manga and art sauce! Got a screenshot of an anime but don't know where it's from? A manga page from a meme? A piece of art you love but don't know who made it? Look it up here!",
};

export default function RootLayout({ children }) {
    return (
        <html lang="en">
            <body
                className={`${Caturday.variable}`}
            >
                {children}
            </body>
        </html>
    );
}
