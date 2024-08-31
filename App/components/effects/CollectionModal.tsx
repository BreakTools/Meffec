import {
    View,
    Text,
    Modal,
    StyleSheet,
    TouchableOpacity,
    ScrollView,
    TextInput,
} from "react-native";
import MeffecButton from "../styling/MeffecButton";
import { useEffect, useRef, useState } from "react";
import AsyncStorage from "@react-native-async-storage/async-storage";
import CollectionDisplay from "./CollectionDisplay";

interface CollectionModalProps {
    visible: boolean;
    collectionEditInformation: Array<string>;
    closeCollectionEditor: () => void;
}

export default function CollectionModal({
    visible,
    collectionEditInformation,
    closeCollectionEditor,
}: CollectionModalProps) {
    const [availableCollections, setAvailableCollections] = useState<string[]>(
        []
    );
    const [allCollections, setAllCollections] = useState<any>({});
    const newCollectionName = useRef("");

    const effectCategory = collectionEditInformation[0];
    const effectName = collectionEditInformation[1];
    const effectDescription = collectionEditInformation[2];

    useEffect(() => {
        AsyncStorage.getItem("availableCollections")
            .then((collections) => {
                if (collections) {
                    setAvailableCollections(JSON.parse(collections));
                }
            })
            .catch((error) => {
                console.log("Error fetching collections:", error);
            });

        AsyncStorage.getItem("collections")
            .then((collections) => {
                if (collections) {
                    setAllCollections(JSON.parse(collections));
                }
            })
            .catch((error) => {
                console.log("Error fetching collections:", error);
            });
    }, []);

    function addNewCollection() {
        if (newCollectionName.current === "") {
            return;
        }

        if (availableCollections.includes(newCollectionName.current)) {
            return;
        }

        AsyncStorage.getItem("availableCollections")
            .then((collections) => {
                const updatedCollections = collections
                    ? JSON.parse(collections)
                    : [];
                updatedCollections.push(newCollectionName.current);
                AsyncStorage.setItem(
                    "availableCollections",
                    JSON.stringify(updatedCollections)
                )
                    .then(() => {
                        setAvailableCollections(updatedCollections);
                        console.log("New collection stored successfully");
                    })
                    .catch((error) => {
                        console.log("Error storing new collection:", error);
                    });
            })
            .catch((error) => {
                console.log(error);
            });
    }

    function removeCollection(collectionName: string) {
        AsyncStorage.getItem("availableCollections")
            .then((collections) => {
                const updatedCollections = collections
                    ? JSON.parse(collections)
                    : [];
                const index = updatedCollections.indexOf(collectionName);
                if (index > -1) {
                    updatedCollections.splice(index, 1);
                }
                AsyncStorage.setItem(
                    "availableCollections",
                    JSON.stringify(updatedCollections)
                )
                    .then(() => {
                        setAvailableCollections(updatedCollections);
                        console.log("Collection removed successfully");
                    })
                    .catch((error) => {
                        console.log("Error removing collection:", error);
                    });
            })
            .catch((error) => {
                console.log(error);
            });

        AsyncStorage.getItem("collections").then((collections) => {
            let collectionsData = collections ? JSON.parse(collections) : {};
            console.log(collectionName);
            if (collectionsData) {
                delete collectionsData[collectionName];
                AsyncStorage.setItem(
                    "collections",
                    JSON.stringify(collectionsData)
                )
                    .then(() => {
                        console.log("Collection removed successfully");
                        setAllCollections(collectionsData);
                    })
                    .catch((error) => {
                        console.log("Error removing collection:", error);
                    });
            }
        });
    }

    function configureCollection(
        collectionName: string,
        action: "add" | "remove"
    ) {
        AsyncStorage.getItem("collections")
            .then((collections) => {
                let collectionsData = collections
                    ? JSON.parse(collections)
                    : {};

                if (!collectionsData[collectionName]) {
                    collectionsData[collectionName] = [];
                }

                if (action === "add") {
                    collectionsData[collectionName].push({
                        category: effectCategory,
                        name: effectName,
                        description: effectDescription,
                    });
                } else if (action === "remove") {
                    collectionsData[collectionName] = collectionsData[
                        collectionName
                    ].filter(
                        (effect: any) =>
                            effect.category !== effectCategory ||
                            effect.name !== effectName ||
                            effect.description !== effectDescription
                    );
                }

                AsyncStorage.setItem(
                    "collections",
                    JSON.stringify(collectionsData)
                )
                    .then(() => {
                        console.log(
                            `Collection ${action}ed successfully in ${collectionName}`
                        );
                        setAllCollections(collectionsData);
                    })
                    .catch((error) => {
                        console.log(`Error ${action}ing collection:`, error);
                    });
            })
            .catch((error) => {
                console.log("Error fetching collections:", error);
            });
    }

    return (
        <Modal animationType="fade" transparent={true} visible={visible}>
            <View style={styles.modalView}>
                <View style={styles.collectionModal}>
                    <Text style={styles.collectionsText}>
                        Select collections
                    </Text>
                    <Text style={styles.effectNameText}>
                        {">"} {collectionEditInformation[1]}
                    </Text>
                    <ScrollView style={styles.scrollView}>
                        <View style={styles.collectionContainer}>
                            {availableCollections.map(
                                (collectionName, index) => (
                                    <View
                                        key={index}
                                        style={styles.collectionItem}
                                    >
                                        <CollectionDisplay
                                            collectionName={collectionName}
                                            category={effectCategory}
                                            name={effectName}
                                            removeCollection={removeCollection}
                                            allCollections={allCollections}
                                            configureCollection={
                                                configureCollection
                                            }
                                        />
                                    </View>
                                )
                            )}
                        </View>

                        <View style={styles.newCollectionView}>
                            <TextInput
                                style={[
                                    styles.newCollectionContainer,
                                    styles.textInputWidth,
                                ]}
                                placeholderTextColor={"grey"}
                                placeholder="New collection..."
                                onChangeText={(text) =>
                                    (newCollectionName.current = text)
                                }
                            />
                            <TouchableOpacity
                                onPress={() => addNewCollection()}
                            >
                                <Text style={styles.newCollectionContainer}>
                                    +
                                </Text>
                            </TouchableOpacity>
                        </View>
                    </ScrollView>
                    <View style={styles.bottomButtons}>
                        <TouchableOpacity
                            onPress={() => closeCollectionEditor()}
                        >
                            <MeffecButton text="Done" />
                        </TouchableOpacity>
                    </View>
                </View>
            </View>
        </Modal>
    );
}

const styles = StyleSheet.create({
    modalView: {
        flex: 1,
        backgroundColor: "rgba(0,0,0,0.5)",
        padding: 35,
        alignItems: "center",
        justifyContent: "center",
    },
    collectionModal: {
        backgroundColor: "rgba(0,0,0,0.6)",
        borderWidth: 0.2,
        borderColor: "#FFFFFF",
        borderRadius: 8,
        padding: 14,
        shadowColor: "#FFFFFF",
        shadowOpacity: 0.3,
        shadowRadius: 4,
        elevation: 2,
        marginBottom: 10,
        width: "90%",
        height: "50%",
    },
    collectionContainer: {
        flexDirection: "row",
        flexWrap: "wrap",
        justifyContent: "space-between",
        marginBottom: 15,
        marginTop: 10,
    },
    collectionItem: {
        width: "48%",
    },
    newCollectionContainer: {
        borderWidth: 0.2,
        borderColor: "#FFFFFF",
        borderRadius: 8,
        padding: 6,
        shadowColor: "#FFFFFF",
        shadowOpacity: 0.1,
        shadowRadius: 4,
        elevation: 2,
        color: "#FFFFFF",
        marginHorizontal: 5,
    },
    newCollectionView: {
        flexDirection: "row",
        justifyContent: "center",
        marginTop: 10,
        marginBottom: 30,
    },
    textInputWidth: {
        width: "50%",
    },
    scrollView: {
        flex: 1,
    },
    collectionsText: {
        fontSize: 28,
        textAlign: "left",
        color: "#FFFFFF",
        fontWeight: "600",
        fontFamily: "Inter",
    },
    effectNameText: {
        marginBottom: 5,
        fontSize: 15,
        textAlign: "left",
        color: "#FFFFFF",
        fontWeight: "300",
        fontFamily: "Inter",
    },
    bottomButtons: {
        flexDirection: "row",
        justifyContent: "center",
        marginTop: 10,
    },
});
