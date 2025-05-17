"use client";

import { useState, useEffect } from "react";
import { mcpClient, isMcpError, McpClient } from "@/lib/mcp-client";
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from "./ui/card";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Badge } from "./ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";

// Create local version for UI display since baseUrl is private in the class
const MCP_SERVER_URL = "http://localhost:8000/mcp"; 

export function McpClientTester() {
  const [serverStatus, setServerStatus] = useState<"checking" | "online" | "offline">("checking");
  const [addResult, setAddResult] = useState<number | null>(null);
  const [addError, setAddError] = useState<string | null>(null);
  const [num1, setNum1] = useState<number>(5);
  const [num2, setNum2] = useState<number>(10);
  
  const [name, setName] = useState<string>("world");
  const [greeting, setGreeting] = useState<string | null>(null);
  const [greetingError, setGreetingError] = useState<string | null>(null);
  
  // Check server status on load
  useEffect(() => {
    const checkServerStatus = async () => {
      const isOnline = await mcpClient.ping();
      setServerStatus(isOnline ? "online" : "offline");
    };
    
    checkServerStatus();
    
    // Check again every 10 seconds
    const interval = setInterval(checkServerStatus, 10000);
    
    return () => clearInterval(interval);
  }, []);
  
  const handleAddNumbers = async () => {
    setAddResult(null);
    setAddError(null);
    
    const result = await mcpClient.add(num1, num2);
    
    if (isMcpError(result)) {
      setAddError(result.error);
    } else {
      setAddResult(result);
    }
  };
  
  const handleGetGreeting = async () => {
    setGreeting(null);
    setGreetingError(null);
    
    const result = await mcpClient.getGreeting(name);
    
    if (isMcpError(result)) {
      setGreetingError(result.error);
    } else {
      setGreeting(result);
    }
  };
  
  return (
    <div className="container mx-auto p-4 max-w-2xl">
      <Card className="shadow-md">
        <CardHeader>
          <div className="flex justify-between items-center">
            <CardTitle>MCP Client Tester</CardTitle>
            <Badge 
              variant={
                serverStatus === "online" ? "default" : 
                serverStatus === "offline" ? "destructive" : "outline"
              }
              className={serverStatus === "online" ? "bg-green-500" : undefined}
            >
              {serverStatus === "checking" ? "Checking..." : 
               serverStatus === "online" ? "Server Online" : "Server Offline"}
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="tools">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="tools">Tools</TabsTrigger>
              <TabsTrigger value="resources">Resources</TabsTrigger>
            </TabsList>
            
            <TabsContent value="tools" className="mt-4">
              <div className="space-y-4">
                <h3 className="font-medium">Test Add Tool</h3>
                <div className="flex gap-3 items-center">
                  <Input 
                    type="number" 
                    value={num1} 
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) => setNum1(Number(e.target.value))}
                    className="w-20"
                  />
                  <span>+</span>
                  <Input 
                    type="number" 
                    value={num2} 
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) => setNum2(Number(e.target.value))}
                    className="w-20"
                  />
                  <Button onClick={handleAddNumbers}>Calculate</Button>
                </div>
                
                {addResult !== null && (
                  <div className="bg-primary/10 p-3 rounded border border-primary/30">
                    Result: <span className="font-medium">{addResult}</span>
                  </div>
                )}
                
                {addError && (
                  <div className="bg-destructive/10 p-3 rounded border border-destructive/30 text-destructive">
                    Error: {addError}
                  </div>
                )}
              </div>
            </TabsContent>
            
            <TabsContent value="resources" className="mt-4">
              <div className="space-y-4">
                <h3 className="font-medium">Test Greeting Resource</h3>
                <div className="flex gap-3 items-center">
                  <Input 
                    type="text" 
                    value={name} 
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) => setName(e.target.value)}
                    placeholder="Enter name"
                    className="flex-1"
                  />
                  <Button onClick={handleGetGreeting}>Get Greeting</Button>
                </div>
                
                {greeting && (
                  <div className="bg-primary/10 p-3 rounded border border-primary/30">
                    Greeting: <span className="font-medium">{greeting}</span>
                  </div>
                )}
                
                {greetingError && (
                  <div className="bg-destructive/10 p-3 rounded border border-destructive/30 text-destructive">
                    Error: {greetingError}
                  </div>
                )}
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
        <CardFooter className="bg-muted/30 border-t flex flex-col items-start text-xs p-3">
          <p>MCP Server URL: {MCP_SERVER_URL}</p>
          <p className="mt-1">Note: Make sure the MCP server is running with <code>python server.py http</code></p>
        </CardFooter>
      </Card>
    </div>
  );
} 