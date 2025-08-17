import BigScreenText from "@/components/styling/BigScreenText";
import WebSocketConnectionOverlay from "@/components/websockets/WebsocketConnectionOverlay";
import AsyncStorage from "@react-native-async-storage/async-storage";
import React, { useMemo, useState, useCallback } from "react";
import {
  SafeAreaView,
  Platform,
  StyleSheet,
  View,
  Text,
  ScrollView,
} from "react-native";
import { useFocusEffect } from "@react-navigation/native";
import { Dropdown } from "react-native-element-dropdown";
import CollectedEffectDisplay from "@/components/effects/CollectedEffectDisplay";

export default function CollectionsScreen() {
  const [allCollections, setAllCollections] = useState<Record<string, any>>({});
  const [selectedCollection, setSelectedCollection] = useState<string>("");

  const loadCollections = useCallback(async () => {
    try {
      const raw = await AsyncStorage.getItem("collections");
      const parsed = raw ? JSON.parse(raw) : {};
      if (parsed && typeof parsed === "object") {
        setAllCollections(parsed);
        const keys = Object.keys(parsed);
        if (keys.length === 0) {
          setSelectedCollection("");
        } else if (!keys.includes(selectedCollection)) {
          setSelectedCollection(keys[0]);
        }
      } else {
        setAllCollections({});
        setSelectedCollection("");
      }
    } catch (e) {
      console.log("Error fetching collections:", e);
      setAllCollections({});
      setSelectedCollection("");
    }
  }, [selectedCollection]);

  useFocusEffect(
    useCallback(() => {
      let mounted = true;
      (async () => {
        if (!mounted) return;
        await loadCollections();
      })();
      return () => {
        mounted = false;
      };
    }, [loadCollections])
  );

  const dropDownFormattedData = useMemo(
    () =>
      Object.keys(allCollections).map((key) => ({
        label: key,
        value: key,
      })),
    [allCollections]
  );

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
          value={selectedCollection}
          onFocus={loadCollections}
          onChange={(item: any) => setSelectedCollection(item.value)}
          placeholder="Select collection"
          placeholderStyle={styles.dropdownTitle}
          selectedTextStyle={styles.dropdownTitle}
          containerStyle={styles.dropdownContainerStyle}
          itemTextStyle={styles.itemTextStyle}
          activeColor="rgba(256, 256, 256, 0.2)"
        />
        <ScrollView style={styles.paddedView}>
          {selectedCollection &&
            allCollections[selectedCollection] &&
            Object.keys(allCollections[selectedCollection]).map((effectKey) => {
              const effect = allCollections[selectedCollection][effectKey];
              return (
                <CollectedEffectDisplay
                  key={effectKey}
                  category={effect.category}
                  name={effect.name}
                  description={effect.description}
                />
              );
            })}
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
  content: { flex: 1, justifyContent: "center", alignItems: "center" },
  paddedView: { marginHorizontal: 20 },
  dropdown: { marginHorizontal: 20, marginVertical: 10 },
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
    borderColor: "transparent",
  },
  itemTextStyle: {
    color: "#FFFFFF",
    fontFamily: "Inter",
    fontSize: 14,
    fontWeight: "400",
  },
  noCollectionView: { flex: 1, justifyContent: "center" },
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
