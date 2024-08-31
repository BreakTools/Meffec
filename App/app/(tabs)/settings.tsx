import React, { useState, useEffect, useContext } from "react";
import {
    SafeAreaView,
    Platform,
    StyleSheet,
    View,
    TextInput,
    Alert,
    Text,
    TouchableOpacity,
} from "react-native";
import AsyncStorage from "@react-native-async-storage/async-storage";
import BigScreenText from "@/components/styling/BigScreenText";
import WebSocketConnectionOverlay from "@/components/websockets/WebsocketConnectionOverlay";
import { WebSocketContext } from "@/websockets/WebSocketContext";
import MeffecButton from "@/components/styling/MeffecButton";

export default function EffectsScreen() {
    const [serverUrl, setServerUrl] = useState("");
    const [authToken, setAuthToken] = useState("");
    const websocketContext = useContext(WebSocketContext);

    useEffect(() => {
        const loadSettings = async () => {
            try {
                const savedServerUrl = await AsyncStorage.getItem("serverUrl");
                const savedAuthToken = await AsyncStorage.getItem("authToken");

                if (savedServerUrl) {
                    setServerUrl(savedServerUrl);
                }

                if (savedAuthToken) {
                    setAuthToken(savedAuthToken);
                }
            } catch (error) {
                console.error("Failed to load settings", error);
            }
        };

        loadSettings();
    }, []);

    const saveSettings = async () => {
        try {
            await AsyncStorage.setItem("serverUrl", serverUrl);
            await AsyncStorage.setItem("authToken", authToken);
            Alert.alert("Success", "Settings saved successfully");
        } catch (error) {
            console.error("Failed to save settings", error);
            Alert.alert("Error", "Failed to save settings");
        }
        websocketContext?.reconnect();
    };

    return (
        <SafeAreaView style={styles.container}>
            <WebSocketConnectionOverlay>
                <BigScreenText text="Settings" />

                <View style={styles.paddedView}>
                    <Text style={styles.settingText}>Meffec server URL</Text>
                    <TextInput
                        style={styles.input}
                        placeholder="Server URL"
                        value={serverUrl}
                        onChangeText={setServerUrl}
                        secureTextEntry={false}
                    />
                    <Text style={styles.settingText}>Authentication token</Text>
                    <TextInput
                        style={styles.input}
                        placeholder="Authentication Token"
                        value={authToken}
                        onChangeText={setAuthToken}
                        secureTextEntry={true}
                    />
                    <TouchableOpacity
                        onPress={saveSettings}
                        style={styles.buttonCenterContainer}
                    >
                        <MeffecButton text="Save settings" />
                    </TouchableOpacity>
                </View>
            </WebSocketConnectionOverlay>
        </SafeAreaView>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        paddingTop: Platform.OS === "ios" ? 20 : 0,
        backgroundColor: "#1C1C1C",
    },
    paddedView: {
        marginHorizontal: 20,
        marginTop: 10,
    },
    input: {
        height: 40,
        borderColor: "#ccc",
        borderWidth: 1,
        marginBottom: 12,
        borderRadius: 5,
        paddingHorizontal: 8,
        color: "#FFFFFF",
    },
    settingText: {
        color: "#FFFFFF",
        fontSize: 16,
        fontWeight: "500",
        marginTop: 4,
        marginBottom: 3,
        fontFamily: "Inter",
    },
    buttonCenterContainer: {
        marginTop: 10,
        alignItems: "center",
    },
});
