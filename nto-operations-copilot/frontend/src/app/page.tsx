"use client";

import { useState } from "react";
import { AnimatePresence } from "framer-motion";

import IntroScene from "@/components/nto/IntroScene";
import OperationsWorkspace from "@/components/nto/OperationsWorkspace";

export default function Home() {
  const [entered, setEntered] = useState(false);

  return (
    <main className="min-h-screen bg-[#f8fafc]">
      <AnimatePresence mode="wait">
        {!entered ? (
          <IntroScene
            key="intro"
            onEnter={() => setEntered(true)}
          />
        ) : (
          <OperationsWorkspace key="workspace" />
        )}
      </AnimatePresence>
    </main>
  );
}
