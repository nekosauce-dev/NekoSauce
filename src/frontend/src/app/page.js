"use client";

import Link from "next/link";

import {
    Accordion,
    AccordionContent,
    AccordionItem,
    AccordionTrigger,
} from "@/components/ui/accordion";
import {
    Card,
    CardContent,
    CardDescription,
    CardFooter,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { Progress } from "@/components/ui/progress";
import { Button } from "@/components/ui/button";
import {
    Tooltip,
    TooltipContent,
    TooltipProvider,
    TooltipTrigger,
} from "@/components/ui/tooltip";

export default function Home() {
    return (
        <main className="flex flex-col items-center justify-center py-8 px-4 min-h-full selection:bg-rose-400 selection:text-white selection:rounded">
            <div className="w-full max-w-md h-full flex flex-col gap-4 relative">
                <h1 className="font-caturday text-6xl leading-none text-center">
                    NekoSauce
                </h1>
                <p className="text-center text-lg leading-normal text-muted-foreground">
                    Find any anime/manga art's sauce!
                </p>
                <Card className="my-4">
                    <CardHeader>
                        <CardTitle>FAQ</CardTitle>
                        <CardDescription>
                            Frequently Asked Questions
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <Separator />
                        <Accordion type="single" collapsible className="w-full">
                            <AccordionItem value="whats-nekosauce">
                                <AccordionTrigger>
                                    What's NekoSauce?
                                </AccordionTrigger>
                                <AccordionContent>
                                    NekoSauce is an anime/manga art/screenshot
                                    sauce finder tool. It was made to help
                                    people find artists from their artworks,
                                    specifically targeting anime/manga art. It
                                    was made to help both users and developers
                                    who want to implement an API like this one
                                    in their apps.
                                </AccordionContent>
                            </AccordionItem>
                            <AccordionItem value="when-will-nekosauce-be-released">
                                <AccordionTrigger>
                                    When will NekoSauce be released?
                                </AccordionTrigger>
                                <AccordionContent>
                                    NekoSauce is currently fetching sauces
                                    (again) and hashing them. Ideally a beta
                                    will be released once it reaches around
                                    8,000,000 hashed sauces, but it's not
                                    confirmed.
                                </AccordionContent>
                            </AccordionItem>
                            <AccordionItem value="where-are-the-sauces-taken-from">
                                <AccordionTrigger>
                                    Where are the sauces taken from?
                                </AccordionTrigger>
                                <AccordionContent>
                                    At the time of writing, the supported
                                    sources are: Danbooru, Gelbooru, Konachan,
                                    and Yande.re. I'm constantly adding new
                                    sources, so stay tuned!
                                </AccordionContent>
                            </AccordionItem>
                            <AccordionItem value="why-nekosauce">
                                <AccordionTrigger>
                                    Why NekoSauce?
                                </AccordionTrigger>
                                <AccordionContent>
                                    NekoSauce has a bunch of nice features that
                                    are not available in other sauce finders.
                                    Image tagging, fast queries and search
                                    customization are just a few of them!
                                </AccordionContent>
                            </AccordionItem>
                            <AccordionItem value="is-it-open-source">
                                <AccordionTrigger>
                                    Is it open source?
                                </AccordionTrigger>
                                <AccordionContent>
                                    Currently, the source code is only open to
                                    donators. This could change in the future,
                                    but I need to confirm a few things before
                                    completely open-sourcing it.
                                </AccordionContent>
                            </AccordionItem>
                            <AccordionItem value="will-i-need-to-pay">
                                <AccordionTrigger>
                                    Will I need to pay?
                                </AccordionTrigger>
                                <AccordionContent>
                                    NekoSauce is 100% free to use for regular
                                    users! The API is a bit more limited since
                                    the servers are not yet prepared to receive
                                    big amounts of requests. Donators have an{" "}
                                    <b>increased limit</b>.
                                </AccordionContent>
                            </AccordionItem>
                        </Accordion>
                    </CardContent>
                    {process.env.FUNDING_PROGRESS && (
                        <CardFooter className="flex items-center gap-2">
                            <Progress
                                value={process.env.FUNDING_PROGRESS}
                                className="flex-1"
                            />
                            <div className="text-muted-foreground">
                                {process.env.FUNDING_PROGRESS_FORMAT.replace(
                                    "{value}",
                                    process.env.FUNDING_PROGRESS
                                )}{" "}
                                funded
                            </div>
                        </CardFooter>
                    )}
                </Card>
                <div className="flex flex-row items-center justify-center">
                    {process.env.FOOTER_DISCORD_LINK && (
                        <>
                            <Link
                                href={process.env.FOOTER_DISCORD_LINK}
                                target="_blank"
                                key="discord-btn"
                            >
                                <Button variant="link">Discord</Button>
                            </Link>
                            <Separator
                                key="discord-separator"
                                orientation="vertical"
                                className="h-6"
                            />
                        </>
                    )}
                    {process.env.FOOTER_TWITTER_LINK && (
                        <>
                            <Link
                                href={process.env.FOOTER_TWITTER_LINK}
                                target="_blank"
                                key="twitter-btn"
                            >
                                <Button variant="link">Twitter</Button>
                            </Link>
                            <Separator
                                key="twitter-separator"
                                orientation="vertical"
                                className="h-6"
                            />
                        </>
                    )}
                    {process.env.FOOTER_REDDIT_LINK && (
                        <>
                            <Link
                                href={process.env.FOOTER_REDDIT_LINK}
                                target="_blank"
                                key="reddit-btn"
                            >
                                <Button variant="link">Reddit</Button>
                            </Link>
                            <Separator
                                key="reddit-separator"
                                orientation="vertical"
                                className="h-6"
                            />
                        </>
                    )}
                    {process.env.FOOTER_DONATE_LINK && (
                        <>
                            <TooltipProvider>
                                <Tooltip>
                                    <TooltipTrigger asChild>
                                        <Link
                                            href={
                                                process.env.FOOTER_DONATE_LINK
                                            }
                                            target="_blank"
                                            key="donate-btn"
                                        >
                                            <Button variant="link">
                                                Donate
                                            </Button>
                                        </Link>
                                    </TooltipTrigger>
                                    {process.env.FUNDING_PROGRESS && (
                                        <TooltipContent>
                                            <p>
                                                {process.env.FUNDING_PROGRESS_FORMAT.replace(
                                                    "{value}",
                                                    process.env.FUNDING_PROGRESS
                                                )}{" "}
                                                funded
                                            </p>
                                        </TooltipContent>
                                    )}
                                </Tooltip>
                            </TooltipProvider>
                            <Separator
                                key="donate-separator"
                                orientation="vertical"
                                className="h-6"
                            />
                        </>
                    )}
                    <Link
                        href="https://nyeki.dev"
                        target="_blank"
                        key="nyeki-btn"
                    >
                        <Button variant="link">Nyeki.py</Button>
                    </Link>
                </div>
            </div>
        </main>
    );
}
