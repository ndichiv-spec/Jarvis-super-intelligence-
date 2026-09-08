/**
 * JARVIS Voice Control Panel
 * ===========================
 * Tony Stark-inspired voice interface control.
 * Talk to JARVIS naturally - "JARVIS, run diagnostics"
 * 
 * Features:
 * - Real-time voice chat via WebSocket
 * - Text-to-Speech (TTS) controls
 * - Speech-to-Text (ASR) controls
 * - Voice profile management
 * - Live conversation history
 */

"use client";

import { useState, useEffect, useRef } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Mic,
  MicOff,
  Volume2,
  VolumeX,
  MessageSquare,
  Settings,
  Play,
  Square,
  Phone,
  PhoneOff,
  Activity,
} from "lucide-react";
import { toast } from "sonner";
import { jarvisAPI } from "@/lib/api";

interface VoiceMessage {
  id: string;
  type: "user" | "assistant" | "system";
  text: string;
  timestamp: Date;
  confidence?: number;
  engine?: string;
}

interface VoiceStatus {
  is_initialized: boolean;
  tts_available: boolean;
  asr_available: boolean;
  whisper_available: boolean;
  continuous_listening: boolean;
  listener_count: number;
}

export default function VoiceControlPanel() {
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [messages, setMessages] = useState<VoiceMessage[]>([]);
  const [inputText, setInputText] = useState("");
  const [voiceStatus, setVoiceStatus] = useState<VoiceStatus | null>(null);
  const [activeProfile, setActiveProfile] = useState<string>("jarvis_default");
  const wsRef = useRef<WebSocket | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Fetch voice status on mount
  useEffect(() => {
    fetchVoiceStatus();
  }, []);

  // Auto-scroll messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const fetchVoiceStatus = async () => {
    try {
      const status = await jarvisAPI.voiceGetStatus();
      if (status.success) {
        setVoiceStatus(status.status);
      }
    } catch (error) {
      console.error("Failed to fetch voice status:", error);
    }
  };

  const connectVoiceWebSocket = () => {
    if (wsRef.current) {
      wsRef.current.close();
    }

    const ws = jarvisAPI.connectVoiceWebSocket(
      (data) => {
        console.log("Voice WS message:", data);

        if (data.status === "listening") {
          setIsListening(true);
          addSystemMessage("Listening...");
        } else if (data.status === "recognized") {
          setIsListening(false);
          addMessage({
            type: "user",
            text: data.text,
            confidence: data.confidence,
            engine: data.engine,
          });
        } else if (data.status === "response") {
          addMessage({
            type: "assistant",
            text: data.text,
            confidence: data.confidence,
            engine: data.engine,
          });
        } else if (data.status === "speaking") {
          setIsSpeaking(true);
          addSystemMessage("Speaking response...");
        } else if (data.status === "complete") {
          setIsSpeaking(false);
          setIsListening(false);
          addSystemMessage("Conversation complete");
        } else if (data.status === "error") {
          setIsListening(false);
          setIsSpeaking(false);
          addSystemMessage(`Error: ${data.error}`);
          toast.error(`Voice error: ${data.error}`);
        }
      },
      (error) => {
        console.error("Voice WebSocket error:", error);
        setIsConnected(false);
        toast.error("Voice connection lost");
      }
    );

    wsRef.current = ws;
    setIsConnected(true);
    toast.success("Voice connection established");
  };

  const disconnectVoiceWebSocket = () => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setIsConnected(false);
    setIsListening(false);
    setIsSpeaking(false);
    toast.info("Voice connection closed");
  };

  const addMessage = (msg: Omit<VoiceMessage, "id" | "timestamp">) => {
    const newMessage: VoiceMessage = {
      ...msg,
      id: Date.now().toString(),
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, newMessage]);
  };

  const addSystemMessage = (text: string) => {
    addMessage({
      type: "system",
      text,
    });
  };

  const handleStartListening = () => {
    if (!wsRef.current) {
      connectVoiceWebSocket();
    }

    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(
        JSON.stringify({
          action: "listen",
          timeout: 5,
          phrase_time_limit: 10,
        })
      );
    } else {
      toast.error("Voice connection not ready");
    }
  };

  const handleSpeakText = async () => {
    if (!inputText.trim()) {
      toast.error("Please enter text to speak");
      return;
    }

    try {
      setIsSpeaking(true);
      await jarvisAPI.voiceSpeak(inputText, activeProfile);
      addMessage({
        type: "assistant",
        text: inputText,
      });
      setIsSpeaking(false);
      toast.success("Speaking...");
    } catch (error: any) {
      setIsSpeaking(false);
      toast.error(`Failed to speak: ${error.message}`);
    }
  };

  const handleManualListen = async () => {
    try {
      setIsListening(true);
      const result = await jarvisAPI.voiceListen(5, 10);
      setIsListening(false);

      if (result.success) {
        addMessage({
          type: "user",
          text: result.text,
          confidence: result.confidence,
          engine: result.engine,
        });

        // Process through AI
        const aiResponse = await jarvisAPI.starkChat({
          message: result.text,
        });

        if (aiResponse.success) {
          addMessage({
            type: "assistant",
            text: aiResponse.response,
            confidence: aiResponse.confidence,
            engine: aiResponse.engine,
          });

          // Speak response
          await jarvisAPI.voiceSpeak(aiResponse.response);
        }
      } else {
        toast.error(result.error || "Listen failed");
      }
    } catch (error: any) {
      setIsListening(false);
      toast.error(`Listen failed: ${error.message}`);
    }
  };

  const clearConversation = () => {
    setMessages([]);
    toast.info("Conversation cleared");
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
            JARVIS Voice Interface
          </h1>
          <p className="text-muted-foreground mt-1">
            "Jarvis, run diagnostics" - Tony Stark
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="outline" className="px-3 py-1">
            <div
              className={`h-2 w-2 rounded-full mr-2 ${
                isConnected ? "bg-green-500 animate-pulse" : "bg-gray-500"
              }`}
            ></div>
            {isConnected ? "Connected" : "Disconnected"}
          </Badge>
          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              fetchVoiceStatus();
              toast.success("Status refreshed");
            }}
          >
            Refresh
          </Button>
        </div>
      </div>

      {/* Voice Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="border-blue-500/20">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Volume2 className="h-4 w-4 text-blue-400" />
              TTS Engine
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Badge
              variant="outline"
              className={
                voiceStatus?.tts_available
                  ? "border-green-500 text-green-400"
                  : "border-red-500 text-red-400"
              }
            >
              {voiceStatus?.tts_available ? "Online" : "Offline"}
            </Badge>
          </CardContent>
        </Card>

        <Card className="border-purple-500/20">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Mic className="h-4 w-4 text-purple-400" />
              ASR Engine
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Badge
              variant="outline"
              className={
                voiceStatus?.asr_available
                  ? "border-green-500 text-green-400"
                  : "border-red-500 text-red-400"
              }
            >
              {voiceStatus?.asr_available ? "Online" : "Offline"}
            </Badge>
          </CardContent>
        </Card>

        <Card className="border-cyan-500/20">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Activity className="h-4 w-4 text-cyan-400" />
              Whisper
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Badge
              variant="outline"
              className={
                voiceStatus?.whisper_available
                  ? "border-green-500 text-green-400"
                  : "border-yellow-500 text-yellow-400"
              }
            >
              {voiceStatus?.whisper_available ? "Available" : "Fallback"}
            </Badge>
          </CardContent>
        </Card>

        <Card className="border-green-500/20">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <MessageSquare className="h-4 w-4 text-green-400" />
              Messages
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-green-400">
              {messages.length}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              in conversation
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Voice Chat */}
        <Card className="lg:col-span-2 border-blue-500/20">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Phone className="h-5 w-5 text-blue-400" />
              Voice Chat
              {isListening && (
                <Badge variant="destructive" className="ml-2 animate-pulse">
                  <Mic className="h-3 w-3 mr-1" />
                  Listening
                </Badge>
              )}
              {isSpeaking && (
                <Badge variant="secondary" className="ml-2 animate-pulse">
                  <Volume2 className="h-3 w-3 mr-1" />
                  Speaking
                </Badge>
              )}
            </CardTitle>
            <CardDescription>
              Talk to JARVIS naturally - voice commands and responses
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Connection Controls */}
            <div className="flex gap-2">
              {!isConnected ? (
                <Button onClick={connectVoiceWebSocket} className="flex-1">
                  <Phone className="h-4 w-4 mr-2" />
                  Connect Voice
                </Button>
              ) : (
                <Button
                  onClick={disconnectVoiceWebSocket}
                  variant="destructive"
                  className="flex-1"
                >
                  <PhoneOff className="h-4 w-4 mr-2" />
                  Disconnect
                </Button>
              )}
              <Button variant="outline" onClick={clearConversation}>
                Clear
              </Button>
            </div>

            {/* Voice Controls */}
            <div className="flex gap-2">
              <Button
                onClick={handleStartListening}
                disabled={!isConnected || isListening}
                variant={isListening ? "destructive" : "default"}
                className="flex-1"
              >
                {isListening ? (
                  <>
                    <MicOff className="h-4 w-4 mr-2" />
                    Listening...
                  </>
                ) : (
                  <>
                    <Mic className="h-4 w-4 mr-2" />
                    Start Listening
                  </>
                )}
              </Button>
              <Button
                onClick={handleManualListen}
                disabled={isListening}
                variant="outline"
              >
                <Mic className="h-4 w-4 mr-2" />
                Quick Listen
              </Button>
            </div>

            {/* Text Input for TTS */}
            <div className="flex gap-2">
              <Input
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                placeholder="Enter text for JARVIS to speak..."
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    handleSpeakText();
                  }
                }}
              />
              <Button
                onClick={handleSpeakText}
                disabled={isSpeaking || !inputText.trim()}
                variant={isSpeaking ? "secondary" : "default"}
              >
                {isSpeaking ? (
                  <>
                    <Square className="h-4 w-4 mr-2" />
                    Speaking
                  </>
                ) : (
                  <>
                    <Play className="h-4 w-4 mr-2" />
                    Speak
                  </>
                )}
              </Button>
            </div>

            {/* Conversation History */}
            <ScrollArea className="h-96 rounded-lg border p-4 bg-muted/30">
              <div className="space-y-3">
                {messages.map((msg) => (
                  <div
                    key={msg.id}
                    className={`flex ${
                      msg.type === "user" ? "justify-end" : "justify-start"
                    }`}
                  >
                    <div
                      className={`max-w-[80%] rounded-lg p-3 ${
                        msg.type === "user"
                          ? "bg-blue-500/20 border border-blue-500/30"
                          : msg.type === "system"
                          ? "bg-gray-500/20 border border-gray-500/30 text-sm italic"
                          : "bg-green-500/20 border border-green-500/30"
                      }`}
                    >
                      <p className="text-sm">{msg.text}</p>
                      <div className="flex items-center gap-2 mt-1 text-xs text-muted-foreground">
                        <span>
                          {msg.timestamp.toLocaleTimeString()}
                        </span>
                        {msg.confidence && (
                          <span>
                            • Confidence: {(msg.confidence * 100).toFixed(0)}%
                          </span>
                        )}
                        {msg.engine && <span>• {msg.engine}</span>}
                      </div>
                    </div>
                  </div>
                ))}
                <div ref={messagesEndRef} />
              </div>
            </ScrollArea>
          </CardContent>
        </Card>

        {/* Voice Settings */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Settings className="h-5 w-5" />
              Voice Settings
            </CardTitle>
            <CardDescription>
              Configure voice profiles and preferences
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Active Profile */}
            <div>
              <label className="text-sm font-medium mb-2 block">
                Active Profile
              </label>
              <Badge variant="secondary" className="px-3 py-1">
                {activeProfile}
              </Badge>
            </div>

            {/* Quick Actions */}
            <div className="space-y-2">
              <Button
                variant="outline"
                className="w-full"
                onClick={async () => {
                  try {
                    const profiles = await jarvisAPI.voiceListProfiles();
                    toast.info(`Found ${profiles.metadata?.profiles?.length || 0} profiles`);
                  } catch (error: any) {
                    toast.error(`Failed: ${error.message}`);
                  }
                }}
              >
                List Voice Profiles
              </Button>
              <Button
                variant="outline"
                className="w-full"
                onClick={async () => {
                  try {
                    const voices = await jarvisAPI.voiceGetVoices();
                    toast.info(`Found ${voices.metadata?.voices?.length || 0} voices`);
                  } catch (error: any) {
                    toast.error(`Failed: ${error.message}`);
                  }
                }}
              >
                Get Available Voices
              </Button>
            </div>

            {/* Voice Info */}
            <div className="rounded-lg border p-3 bg-muted/30 space-y-2">
              <h4 className="font-medium text-sm">Voice Engine Info</h4>
              <div className="space-y-1 text-xs text-muted-foreground">
                <p>• TTS: pyttsx3 (offline)</p>
                <p>• ASR: SpeechRecognition + Whisper</p>
                <p>• Languages: English (more with Whisper)</p>
                <p>• Profiles: Custom voice settings</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
