import React from "react";
import { ScrollText } from "lucide-react";
import PagePlaceholder from "@/components/common/PagePlaceholder";

export default function Summaries() {
  return (
    <PagePlaceholder
      icon={ScrollText}
      title="Summaries"
      description="Generate structured, citation-backed syntheses from your selected materials."
      badge="Coming soon"
    />
  );
}