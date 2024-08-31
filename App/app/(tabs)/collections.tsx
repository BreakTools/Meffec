import BigScreenText from "@/components/styling/BigScreenText";
import WebSocketConnectionOverlay from "@/components/websockets/WebsocketConnectionOverlay";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { useEffect, useState } from "react";
import {
    SafeAreaView,
    Platform,
    StyleSheet,
    View,
    Text,
    ScrollView,
} from "react-native";
import { Dropdown } from "react-native-element-dropdown";
import CollectedEffectDisplay from "@/components/effects/CollectedEffectDisplay";
import { useFocusEffect } from "@react-navigation/native";

export default function CollectionsScreen() {
    const [allCollections, setAllCollections] = useState<any>({});
    const [selectedCollection, setSelectedCollection] = useState<string>("");
    var dropDownFormattedData: any = [];

    if (allCollections && typeof allCollections === "object") {
        dropDownFormattedData = Object.keys(allCollections).map((key) => {
            return {
                label: key,
                value: key,
            };
        });
    }

    function getCollections() {
        AsyncStorage.getItem("collections")
            .then((collections) => {
                if (collections) {
                    const parsedCollections = JSON.parse(collections);
                    if (
                        parsedCollections &&
                        parsedCollections !== allCollections
                    ) {
                        setAllCollections(parsedCollections);
                    }
                }
            })
            .catch((error) => {
                console.log("Error fetching collections:", error);
            });
    }

    useEffect(() => {
        getCollections();
    }, []);

    useFocusEffect(() => {
        getCollections();
    });

    if (Object.keys(allCollections).length === 0) {
        return (
            <SafeAreaView style={styles.container}>
                <WebSocketConnectionOverlay>
                    <BigScreenText text="Collections" />
                    <View style={styles.noCollectionView}>
                        <Text style={styles.noCollectionText}>
                            You have not yet made any collections.
                        </Text>
                    </View>
                </WebSocketConnectionOverlay>
            </SafeAreaView>
        );
    }

    return (
        <SafeAreaView style={styles.container}>
            <WebSocketConnectionOverlay>
                <BigScreenText text="Collections" />
                <Dropdown
                    style={styles.dropdown}
                    data={dropDownFormattedData}
                    labelField="label"
                    valueField="value"
                    onChange={(item: any) => {
                        setSelectedCollection(item.value);
                    }}
                    value={selectedCollection}
                    placeholder="Select collection"
                    placeholderStyle={styles.dropdownTitle}
                    selectedTextStyle={styles.dropdownTitle}
                    containerStyle={styles.dropdownContainerStyle}
                    itemTextStyle={styles.itemTextStyle}
                    activeColor="rgba(256, 256, 256, 0.2)"
                ></Dropdown>
                <ScrollView style={styles.paddedView}>
                    {selectedCollection &&
                        allCollections[selectedCollection] &&
                        Object.keys(allCollections[selectedCollection]).map(
                            (effectKey) => {
                                const effect =
                                    allCollections[selectedCollection][
                                        effectKey
                                    ];
                                return (
                                    <CollectedEffectDisplay
                                        key={effectKey}
                                        category={effect.category}
                                        name={effect.name}
                                        description={effect.description}
                                    />
                                );
                            }
                        )}
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
    dropdown: {
        marginHorizontal: 20,
        marginVertical: 10,
    },
    dropdownTitle: {
        color: "#FFFFFF",
        fontFamily: "Inter",
        fontSize: 24,
        fontWeight: "500",
    },
    dropdownContainerStyle: {
        backgroundColor: "rgba(0, 0, 0, 0.5)",
        shadowColor: "#000000",
        shadowOpacity: 0.6,
        shadowRadius: 15,
        borderColor: "#rgba(256, 256, 256, 0)",
    },
    itemTextStyle: {
        color: "#FFFFFF",
        fontFamily: "Inter",
        fontSize: 14,
        fontWeight: "400",
    },
    noCollectionView: {
        flex: 1,
        justifyContent: "center",
    },
    noCollectionText: {
        color: "#FFFFFF",
        fontFamily: "Inter",
        fontSize: 16,
        fontWeight: "300",
        textAlign: "center",
        width: "60%",
        alignSelf: "center",
    },
});
