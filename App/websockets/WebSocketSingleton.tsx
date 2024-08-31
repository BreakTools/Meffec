import AsyncStorage from "@react-native-async-storage/async-storage";

export class WebSocketSingleton {
    private static instance: WebSocket | null = null;

    private constructor() {}

    public static async getInstance(): Promise<WebSocket | null> {
        if (!WebSocketSingleton.instance) {
            const savedServerUrl = await AsyncStorage.getItem("serverUrl");
            const savedAuthToken = await AsyncStorage.getItem("authToken");
            var constructedUrl: string = "";

            if (savedServerUrl != null || savedAuthToken != null) {
                constructedUrl = `${savedServerUrl}/?token=$${savedAuthToken}`;
            }

            WebSocketSingleton.instance = new WebSocket(constructedUrl);
        }
        return WebSocketSingleton.instance;
    }

    public static closeConnection() {
        WebSocketSingleton.instance?.close();
        WebSocketSingleton.instance = null;
    }
}
