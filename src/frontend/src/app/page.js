"use client";

import { ChevronDownIcon } from "@heroicons/react/24/outline";
import React from "react";

export default function Home() {
    return (
        <main className="flex flex-col items-center justify-center py-8 px-4 min-h-full selection:bg-rose-400 selection:text-white selection:rounded">
            <div className="w-full max-w-md h-full flex flex-col gap-4">
                <h1 className="font-caturday text-6xl leading-none text-center">
                    NekoSauce
                </h1>
                <p className="text-center text-lg leading-normal text-neutral-600">
                    Find any anime/manga art's sauce!
                </p>
                {/* <div className="my-12 flex flex-col gap-2 justify-self-center align-middle">
                    <div className="flex flex-row items-center gap-2 text-xs text-neutral-500 select-none">
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
                                <option value="3">Differential</option>
                                <option value="4">Wavelet</option>
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
                </div> */}
                <div className="mt-8 mb-4">
                    <h1 className="font-bold text-center text-3xl">Frequently Asked Questions</h1>
                </div>
                <div className="flex flex-col gap-4">
                    <FaqItem
                        title="What's NekoSauce?"
                        description="NekoSauce is an anime/manga art/screenshot sauce finder tool. It was made to help people find artists from their artworks, specifically targeting anime/manga art. It was made to help both users and developers who want to implement an API like this one in their apps."
                    />
                    <FaqItem
                        title="When will NekoSauce be released?"
                        description="NekoSauce is ready to be launched! However, it's a project that requires a server with a lot of resources, which I'm not yet ready to pay for. If you want to, you can donate at https://ko-fi.com/nekidev to help this project be released sooner!" />
                    <FaqItem
                        title="Where are the sauces taken from?"
                        description="Currently, only Gelbooru and Danbooru are supported. I'm currently working to bring more sources in the future!" />
                    <FaqItem
                        title="Why NekoSauce?"
                        description="NekoSauce has a bunch of nice features that are not available in other sauce finders. Image tagging, fast queries and search customization are just a few of them!" />
                    <FaqItem
                        title="Is it open source?"
                        description="Currently, it is not. However, I'm probably going to open source it in the future!" />
                    <FaqItem
                        title="Do I have to pay to use NekoSauce?"
                        description="Absolutely not! This is definetly not a project intended to make money. This is just a hobby project I'm working on. However, since the project (and each query) consumes A LOT of resources, I'm not yet ready to pay for the hosting (to be specific, the project will need around 25 USD per month to be released). If you want to, you can donate at https://ko-fi.com/nekidev to help this project be released sooner!" />
                    <FaqItem
                        title="How frequently are sauces updated?"
                        description="Sauces are updated every 30 minutes. They're currently being updated even if the project is not released to public, so that when the release comes the database is full of sauces :)" />
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
