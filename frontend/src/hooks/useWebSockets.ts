import { useEffect, useRef, useState, useCallback } from 'react';

type WebSocketMessage = {
  event_type: string;
  data: any;
};

const MAX_RECONNECT_DELAY = 30000;
const INITIAL_RECONNECT_DELAY = 1000;

export const useWebSockets = (url: string) => {
  const [messages, setMessages] = useState<WebSocketMessage[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const ws = useRef<WebSocket | null>(null);
  const reconnectDelay = useRef(INITIAL_RECONNECT_DELAY);
  const reconnectTimer = useRef<NodeJS.Timeout | null>(null);
  const isMounted = useRef(true);

  function connect() {
    if (typeof window === 'undefined' || !url) return;
    
    // Close existing connection
    if (ws.current) {
      ws.current.close();
    }

    try {
      ws.current = new WebSocket(url);
    } catch (e) {
      console.error("WebSocket connection failed", e);
      scheduleReconnect();
      return;
    }

    ws.current.onopen = () => {
      console.log("WebSocket Connected");
      setIsConnected(true);
      reconnectDelay.current = INITIAL_RECONNECT_DELAY; // Reset delay on success
    };

    ws.current.onmessage = (event) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data);
        setMessages((prev) => [message, ...prev].slice(0, 50));
      } catch (e) {
        console.error("Failed to parse WebSocket message", e);
      }
    };

    ws.current.onclose = () => {
      console.log("WebSocket Disconnected");
      setIsConnected(false);
      if (isMounted.current) {
        scheduleReconnect();
      }
    };

    ws.current.onerror = () => {
      console.error(`WebSocket connection error. Failed to connect to: ${url}`);
      ws.current?.close();
    };
  }

  function scheduleReconnect() {
    if (reconnectTimer.current) clearTimeout(reconnectTimer.current);
    
    reconnectTimer.current = setTimeout(() => {
      if (isMounted.current) {
        console.log(`WebSocket reconnecting in ${reconnectDelay.current}ms...`);
        reconnectDelay.current = Math.min(reconnectDelay.current * 2, MAX_RECONNECT_DELAY);
        connect();
      }
    }, reconnectDelay.current);
  }

  useEffect(() => {
    isMounted.current = true;
    connect();

    return () => {
      isMounted.current = false;
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current);
      if (ws.current) {
        ws.current.close();
      }
    };
  }, [url]);

  return { messages, isConnected };
};
