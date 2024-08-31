import BigScreenText from "@/components/styling/BigScreenText";
import { WebSocketContext } from "@/websockets/WebSocketContext";
import { useContext, useState } from "react";
import {
    SafeAreaView,
    Text,
    Platform,
    StyleSheet,
    ScrollView,
    View,
    RefreshControl,
    Image,
} from "react-native";
import CategoryDisplay from "@/components/effects/CategoryDisplay";
import WebSocketConnectionOverlay from "@/components/websockets/WebsocketConnectionOverlay";
import CollectionModal from "@/components/effects/CollectionModal";

export default function EffectsScreen() {
    const websocketContext = useContext(WebSocketContext);
    const [collectionEditorVisible, setCollectionEditorVisible] =
        useState(false);
    const [collectionEditInformation, setCollectionEditInformation] = useState([
        "",
        "",
    ]);

    if (websocketContext?.storedEffects === null) {
        return (
            <SafeAreaView style={styles.container}>
                <WebSocketConnectionOverlay>
                    <View style={styles.unavailableContainer}>
                        <Image
                            style={styles.brokenEffectsImage}
                            source={require("@/assets/icons/brokeneffects.png")}
                        ></Image>
                        <Text style={styles.unavailableText}>
                            No effects available.
                        </Text>
                    </View>
                </WebSocketConnectionOverlay>
            </SafeAreaView>
        );
    }

    function openCollectionEditor(
        category: string,
        name: string,
        description: string
    ) {
        setCollectionEditInformation([category, name, description]);
        setCollectionEditorVisible(true);
    }

    function closeCollectionEditor() {
        setCollectionEditorVisible(false);
    }

    return (
        <SafeAreaView style={styles.container}>
            <WebSocketConnectionOverlay>
                <CollectionModal
                    visible={collectionEditorVisible}
                    collectionEditInformation={collectionEditInformation}
                    closeCollectionEditor={closeCollectionEditor}
                ></CollectionModal>
                <BigScreenText text="All effects" />

                <ScrollView
                    refreshControl={
                        <RefreshControl
                            refreshing={false}
                            onRefresh={websocketContext?.reconnect}
                        />
                    }
                >
                    <View style={styles.paddedView}>
                        {websocketContext?.storedEffects.map(
                            (category: any) => (
                                <CategoryDisplay
                                    key={category.name}
                                    name={category.name}
                                    effects={category.effects}
                                    openCollectionEditor={openCollectionEditor}
                                />
                            )
                        )}
                    </View>
                </ScrollView>
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
    content: {
        flex: 1,
        justifyContent: "center",
        alignItems: "center",
    },
    paddedView: {
        marginHorizontal: 20,
    },
    unavailableText: {
        color: "#FFFFFF",
        fontWeight: "600",
        fontSize: 16,
        fontFamily: "Inter",
    },
    unavailableContainer: {
        justifyContent: "center",
        alignItems: "center",
        flex: 1,
    },
    brokenEffectsImage: {
        marginBottom: 10,
        width: 50,
        height: 50,
    },
});
