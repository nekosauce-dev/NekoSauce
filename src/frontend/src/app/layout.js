import "./globals.css";
import localFont from "next/font/local";
import { Nunito_Sans } from "next/font/google";

const Caturday = localFont({
    src: "Caturday.ttf",
    variable: "--font-caturday",
    display: "swap",
});

const NunitoSans = Nunito_Sans({
    subsets: ["latin"],
    variable: "--font-nunito-sans",
    display: "swap",
})

export const metadata = {
    title: "NekoSauce - Anime/manga art sauce finder",
    description: "Find your anime/manga art sauce!",
};

export default function RootLayout({ children }) {
    return (
        <html lang="en">
            <body className={`${Caturday.variable} ${NunitoSans.variable} font-nunito`}>{children}</body>
        </html>
    );
}
