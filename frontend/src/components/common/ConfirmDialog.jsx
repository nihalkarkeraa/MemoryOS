import React from "react";
import {
  AlertDialog,
  AlertDialogContent,
  AlertDialogHeader,
  AlertDialogFooter,
  AlertDialogTitle,
  AlertDialogDescription,
  AlertDialogAction,
  AlertDialogCancel,
} from "@/components/ui/alert-dialog";

export default function ConfirmDialog({
  open,
  onOpenChange,
  title,
  message,
  confirmLabel = "Confirm",
  cancelLabel = "Cancel",
  destructive = false,
  onConfirm,
}) {
  return (
    <AlertDialog open={open} onOpenChange={onOpenChange}>
      <AlertDialogContent className="border-border bg-popover">
        <AlertDialogHeader>
          <AlertDialogTitle className="text-[16px] font-semibold tracking-tight text-foreground">
            {title}
          </AlertDialogTitle>
          <AlertDialogDescription className="text-[13.5px] leading-relaxed text-muted-foreground">
            {message}
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel className="border-border bg-transparent text-muted-foreground hover:bg-muted hover:text-foreground">
            {cancelLabel}
          </AlertDialogCancel>
          <AlertDialogAction
            onClick={onConfirm}
            className={
              destructive
                ? "bg-destructive text-destructive-foreground hover:bg-destructive/90"
                : "bg-primary text-primary-foreground hover:bg-primary/90"
            }
          >
            {confirmLabel}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}