export function LoadingScreen() {
  return (
    <div className="flex h-screen items-center justify-center bg-background">
      <div className="flex flex-col items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary text-sm font-bold text-primary-foreground animate-pulse">
          JS
        </div>
        <p className="text-sm text-muted-foreground">Loading JARVIS Studio...</p>
      </div>
    </div>
  );
}
