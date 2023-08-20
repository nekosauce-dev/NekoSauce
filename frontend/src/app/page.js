"use client";

import { ChevronDownIcon } from "@heroicons/react/24/outline";
import React from "react";

export default function Home() {
    return (
        <main className="flex flex-col items-center justify-center p-8 min-h-full selection:bg-rose-400 selection:text-white selection:rounded">
            <div className="w-full max-w-md h-full flex flex-col gap-4">
                <h1 className="font-caturday text-6xl leading-none text-center">
                    NekoSauce
                </h1>
                <p className="text-center text-lg leading-normal text-neutral-600">
                    Find any anime/manga art's sauce!
                </p>
                <div className="my-12 flex flex-col gap-2 justify-self-center align-middle">
                    <div className="flex flex-row items-center gap-2 text-xs text-neutral-500 select-none">
                        <div className="flex flex-row items-center gap-1">
                            <input
                                type="checkbox"
                                className="accent-rose-500"
                                id="crop-resistant"
                                defaultValue={false}
                            />
                            <label for="crop-resistant">Crop resistant</label>
                        </div>
                        <span>/</span>
                        <div className="flex flex-row items-center gap-1">
                            <input
                                type="checkbox"
                                className="accent-rose-500"
                                id="ignore-colors"
                                defaultValue={true}
                            />
                            <label for="ignore-colors">Ignore colors</label>
                        </div>
                        <span>/</span>
                        <div div className="flex flex-row items-center gap-1">
                            <label for="hash" className="text-neutral-600">
                                Hash:
                            </label>
                            <select
                                className="border-none appearance-none p-1 -m-1 outline-none bg-transparent"
                                id="hash"
                            >
                                <option value="1">Perceptual</option>
                                <option value="2">Average</option>
                                <option value="3">Diferential</option>
                            </select>
                            <ChevronDownIcon className="w-3 h-3" />
                        </div>
                        <span>/</span>
                        <div div className="flex flex-row items-center gap-1">
                            <label for="bits" className="text-neutral-600">
                                Bits:
                            </label>
                            <select
                                className="border-none appearance-none p-1 -m-1 outline-none bg-transparent w-fit"
                                id="bits"
                            >
                                <option value="8">8</option>
                                <option value="16">16</option>
                                <option value="32">32</option>
                                <option value="64">64</option>
                            </select>
                            <ChevronDownIcon className="w-3 h-3" />
                        </div>
                    </div>
                    <div className="flex flex-row items-center gap-2">
                        <input
                            className="flex-1 p-2 leading-none bg-white border border-neutral-200 rounded-lg outline-none placeholder:text-neutral-400 transition focus:border-neutral-400"
                            type="url"
                            placeholder="Paste your image's URL"
                        />
                        <button className="py-2 px-4 font-bold bg-rose-500 hover:bg-rose-600 text-white rounded-lg outline-none transition">
                            Upload
                        </button>
                    </div>
                    <p className="text-sm text-neutral-500 leading-none">
                        You can also paste a Reddit URL, a Twitter url, etc., or
                        drop a file!
                    </p>
                </div>
                <div className="flex flex-col gap-4">
                    <FaqItem
                        title="What's NekoSauce?"
                        description="NekoSauce is an anime/manga art/screenshot sauce finder tool. It was made to help people find artists from their artworks, specifically targeting anime/manga art. It was made to help both users and developers who want to implement an API like this one in their apps."
                    />
                    <FaqItem
                        title="Is it free?"
                        description="All basic features are 100% free and will allow you to make up to 200 lookups per day. If you need more advanced features (transform resistance, more bits, more lookups per day, etc.) or just want to support this project, you can make a donation! You choose how much to contribute and it'll automatically enable all features for a month."
                    />
                    <FaqItem
                        title="What are hashes, bits, and all those alien words?"
                        description={
                            "These are things you can adjust to make the search results better or faster. Hashing algorithms are usually don't affect normal users so the default value should work for most use cases. Bits define how detailed the match will be; the more bits the more precise the match will be. However, more bits can also make the search take longer since more details are taken into account when making the search. Lower bit counts will return not-as-precise results but they'll be faster and it usually works better if you have lower quality images."
                        }
                    />
                    <FaqItem
                        title="Manga pages always return incorrent results."
                        description={
                            "This is probably because you have used a low bit count (bits). For manga/doujinshi pages/screenshots/crops, it's better to have a higher bit count since they're almost all in black and white and therefore all images are \"similar\"."
                        }
                    />
                </div>
            </div>
        </main>
    );
}

function FaqItem({ title, description }) {
    const [isOpen, setIsOpen] = React.useState(false);

    return (
        <button
            className="bg-neutral-100 py-2 px-2.5 rounded-lg flex flex-col gap-2 relative text-neutral-900 group"
            onClick={() => setIsOpen(!isOpen)}
        >
            <div className="flex flex-row items-center justify-between w-full">
                <span className="font-bold">{title}</span>
                <button className="rounded-md bg-purple-500 group-hover:bg-purple-600 transition text-white p-1 aspect-square -m-1">
                    <ChevronDownIcon
                        className={`h-5 w-5 stroke-2 ${
                            isOpen ? "rotate-180" : ""
                        }`}
                    />
                </button>
            </div>
            {isOpen && (
                <p className="text-start text-sm text-neutral-600">
                    {description}
                </p>
            )}
        </button>
    );
}
