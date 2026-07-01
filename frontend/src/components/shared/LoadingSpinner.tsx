export function LoadingSpinner({ size = 32 }: { size?: number }) {
  return (
    <div className="flex items-center justify-center p-8">
      <div
        className="border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin"
        style={{ width: size, height: size }}
      />
    </div>
  );
}
