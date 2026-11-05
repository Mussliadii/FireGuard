"use client";

import dynamic from "next/dynamic";

const FireMap = dynamic(() => import("./Map"), { ssr: false });

export default FireMap;
