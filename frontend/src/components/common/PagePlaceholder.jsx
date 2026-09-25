import React from "react";

export default function PagePlaceholder({ icon: Icon, title, description, badge }) {
  return (
    <div className="mx-auto flex h-full w-full max-w-6xl flex-col px-5 py-8 sm:px-8 sm:py-10">
      <div className="flex flex-1 flex-col items-center justify-center rounded-2xl border border-dashed border-border bg-card/30 px-6 py-16 text-center">
        <div className="flex h-14 w-14 items-center justify-center rounded-2xl border border-border bg-muted/40">
          <Icon className="h-6 w-6 text-primary" />
        </div>
        <h2 className="mt-5 text-xl font-semibold tracking-tight text-foreground">{title}</h2>
        <p className="mt-2 max-w-md text-[14px] leading-relaxed text-muted-foreground">{description}</p>
        {badge && (
          <span className="mt-6 inline-flex items-center rounded-lg border border-border bg-muted/40 px-3 py-1.5 text-[12.5px] font-medium text-muted-foreground">
            {badge}
          </span>
        )}
      </div>
    </div>
  );
}