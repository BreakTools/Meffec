import {
    createContext,
    useEffect,
    useState,
    ReactNode,
    useCallback,
    useRef,
} from "react";
import { WebSocketSingleton } from "./WebSocketSingleton";

interface WebSocketContextType {
    sendMessage: (message: string) => void;
    reconnect: () => void;
    reconnectionDisplayCountdown: number;
    storedEffects: any;
    connected: boolean;
}

export const WebSocketContext = createContext<WebSocketContextType | null>(
    null
);

interface WebSocketProviderProps {
    children: ReactNode;
}

export const WebSocketProvider: React.FC<WebSocketProviderProps> = ({
    children,
}) => {
    const [websocket, setWebsocket] = useState<WebSocket | null>(null);
    const [storedEffects, setStoredEffects] = useState<any>(null);
    const [connected, setConnected] = useState<boolean>(false);
    const [reconnectionDisplayCountdown, setReconnectionDisplayCountdown] =
        useState<number>(3);

    const reconnectionCountdown = useRef<number>(3);
    const reconnectionTries = useRef<number>(0);

    const messageReceived = useCallback((event: MessageEvent) => {
        try {
            const jsonData = JSON.parse(event.data);
            if (
                jsonData.type === "information" &&
                jsonData.data?.type === "available_effects"
            ) {
                setStoredEffects(jsonData.data.data);
            }
        } catch (error) {
            console.error("Failed to parse WebSocket message as JSON:", error);
        }
    }, []);

    function sendMessage(message: string) {
        if (websocket) {
            websocket.send(message);
        }
    }

    function reconnect() {
        reconnectionCountdown.current = 0;
        if (websocket) {
            websocket.close();
        } else {
            WebSocketSingleton.closeConnection();
        }
    }

    useEffect(() => {
        const countdownUntilReconnect = () => {
            if (reconnectionCountdown.current === 0) {
                reconnectionTries.current++;
                connectWebSocket();
            } else {
                reconnectionCountdown.current--;
                setReconnectionDisplayCountdown(reconnectionCountdown.current);
                setTimeout(countdownUntilReconnect, 1000);
            }
        };

        const connectWebSocket = async () => {
            try {
                const websocket = await WebSocketSingleton.getInstance();
                setWebsocket(websocket);

                if (websocket === null) {
                    return;
                }

                websocket.onopen = () => {
                    setConnected(true);
                    reconnectionTries.current = 0;

                    websocket.send(
                        JSON.stringify({
                            type: "authentication",
                            data: { type: "app", name: "App" },
                        })
                    );
                };

                websocket.onclose = () => {
                    setConnected(false);
                    WebSocketSingleton.closeConnection();
                    reconnectionCountdown.current = reconnectionTries.current;
                    countdownUntilReconnect();
                };

                websocket.onmessage = messageReceived;
            } catch (error) {
                console.error("Failed to connect WebSocket", error);
            }
        };

        connectWebSocket();

        return () => {
            WebSocketSingleton.closeConnection();
        };
    }, []);

    return (
        <WebSocketContext.Provider
            value={{
                sendMessage,
                reconnect,
                reconnectionDisplayCountdown,
                storedEffects,
                connected,
            }}
        >
            {children}
        </WebSocketContext.Provider>
    );
};
