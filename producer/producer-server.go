package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"

	"github.com/confluentinc/confluent-kafka-go/kafka"
	"github.com/gorilla/mux"
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

type CompleteTrip struct {
	TripID    string
	StartTime string
	EndTime   string
	Status    string
}

func main() {
	fmt.Println("Producing")
	router := mux.NewRouter()
	router.HandleFunc("/trip", tripHandler).Methods("POST")
	router.HandleFunc("/completeTrip", completeTripHandler).Methods("POST")
	log.Fatal(http.ListenAndServe(":8080", router))
}
func tripHandler(w http.ResponseWriter, r *http.Request) {
	body, err := ioutil.ReadAll(r.Body)
	defer r.Body.Close()
	if err != nil {
		panic(err)
	}
	var trip Trip
	err = json.Unmarshal(body, &trip)
	if err != nil {
		http.Error(w, err.Error(), 500)
		return
	}
	topic := trip.Status
	producer, err := kafka.NewProducer(&kafka.ConfigMap{"bootstrap.servers": "localhost:9092"})
	if err != nil {
		panic(err)
	}
	tripString := string(body)
	producer.Produce(&kafka.Message{
		TopicPartition: kafka.TopicPartition{
			Topic:     &topic,
			Partition: kafka.PartitionAny,
		},
		Value: []byte(tripString),
	}, nil)
	w.Header().Set("content-type", "application/json")
	jsonString, err := json.Marshal(trip)
	if err != nil {
		http.Error(w, err.Error(), 500)
		return
	}
	w.Write(jsonString)
}
func completeTripHandler(w http.ResponseWriter, r *http.Request) {
	body, err := ioutil.ReadAll(r.Body)
	defer r.Body.Close()
	if err != nil {
		panic(err)
	}
	var completeTrip CompleteTrip
	err = json.Unmarshal(body, &completeTrip)
	if err != nil {
		http.Error(w, err.Error(), 500)
		return
	}
	topic := completeTrip.Status
	producer, err := kafka.NewProducer(&kafka.ConfigMap{"bootstrap.servers": "localhost:9092"})
	if err != nil {
		panic(err)
	}
	tripString := string(body)
	producer.Produce(&kafka.Message{
		TopicPartition: kafka.TopicPartition{
			Topic:     &topic,
			Partition: kafka.PartitionAny,
		},
		Value: []byte(tripString),
	}, nil)
	w.Header().Set("content-type", "application/json")
	jsonString, err := json.Marshal(completeTrip)
	if err != nil {
		http.Error(w, err.Error(), 500)
		return
	}
	w.Write(jsonString)
}
