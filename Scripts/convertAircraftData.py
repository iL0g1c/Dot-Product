import json

def main():
    with open("../configs/aircraftClassifications.json") as file:
        data = json.loads(file.read())

    processedData = []
    for key in data:
        data[key]
        processedData.append({
            "id": key,
            "name": data[key]["name"],
            "use": ""
        })

    with open("../configs/aircraftClassifications(processed).json", "w") as file:
        json.dump(processedData, file)

if __name__ in "__main__":
    main()