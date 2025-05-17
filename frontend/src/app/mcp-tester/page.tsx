import { McpClientTester } from "@/components/McpClientTester";

export default function McpTesterPage() {
  return (
    <main className="min-h-screen bg-background p-4">
      <div className="container mx-auto">
        <h1 className="text-3xl font-bold mb-8 text-center">MCP Client Tester</h1>
        <McpClientTester />
      </div>
    </main>
  );
} 