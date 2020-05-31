package main

import (
	"bytes"
	"encoding/csv"
	"encoding/json"
	"fmt"
	"io"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"strconv"
	"time"
)

type Trip struct {
	TripID    string
	VendorID  int
	Datetime  string
	Latitude  float64
	Longitude float64
	Status    string
	Zone      string
}

func main() {
	trips, err := os.Open("../data/trips.csv")
	if err != nil {
		log.Fatal(err)
	}
	tripsCSV := csv.NewReader(trips)
	count := 0
	for {
		count = count + 1
		trip, err := tripsCSV.Read()
		if count == 1 {
			continue
		}
		if err == io.EOF {
			break
		}
		if err != nil {
			log.Fatal(err)
		}
		var tripStruct Trip
		tripStruct.TripID = trip[0]
		tripStruct.VendorID, _ = strconv.Atoi(trip[1])
		tripStruct.Datetime = trip[2]
		tripStruct.Longitude, _ = strconv.ParseFloat(trip[3], 64)
		tripStruct.Latitude, _ = strconv.ParseFloat(trip[4], 64)
		tripStruct.Status = trip[5]
		tripStruct.Zone = trip[6]
		tripBytes, err := json.Marshal(tripStruct)
		if err != nil {
			log.Fatal(err)
		}
		sendRequest(tripBytes)
		time.Sleep(1 * time.Second)
	}
}

func sendRequest(body []byte) {
	response, err := http.Post("http://localhost:8080/trip", "application/json", bytes.NewBuffer(body))
	if err != nil {
		log.Fatal(err)
	}
	defer response.Body.Close()
	tripBytes, err := ioutil.ReadAll(response.Body)
	if err != nil {
		log.Fatal(err)
	}
	fmt.Println(string(tripBytes))
}
