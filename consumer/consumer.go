package main

import (
	"database/sql"
	"encoding/json"
	"fmt"

	"github.com/confluentinc/confluent-kafka-go/kafka"
	_ "github.com/lib/pq"
)

type Trip struct {
	TripID    string
	VendorID  int
	Datetime  string
	Latitude  float64
	Longitude float64
	Status    string
}

const (
	DB_USER     = "postgres"
	DB_PASSWORD = "test"
	DB_NAME     = "postgres"
)

var dbInfo = fmt.Sprintf("user=%s password=%s dbname=%s sslmode=disable", DB_USER, DB_PASSWORD, DB_NAME)
var db, err = sql.Open("postgres", dbInfo)

func main() {
	defer db.Close()
	createTable()
	consume()
}
func createTable() {
	statement := `
		CREATE TABLE IF NOT EXISTS trips (tripID TEXT NOT NULL PRIMARY KEY,
							vendorID INTEGER,
							startTime TEXT,
							startLat NUMERIC,
							startLng NUMERIC,
							endTime TEXT,
							endLat NUMERIC,
							endLng NUMERIC,
							status TEXT
							);`
	_, err := db.Exec(statement)
	if err != nil {
		panic(err)
	}
}

func consume() {
	consumer, err := kafka.NewConsumer(&kafka.ConfigMap{
		"bootstrap.servers": "localhost:9092",
		"group.id":          "group-id-1",
		"auto.offset.reset": "earliest",
	})
	if err != nil {
		panic(err)
	}
	consumer.SubscribeTopics([]string{"start", "end"}, nil)
	for {
		message, err := consumer.ReadMessage(-1)
		if err == nil {
			tripString := string(message.Value)
			saveToDB([]byte(tripString))
		} else {
			break
		}
	}
	consumer.Close()
}

func saveToDB(tripBytes []byte) {
	// fmt.Println(string(tripBytes))
	var trip Trip
	err := json.Unmarshal(tripBytes, &trip)
	if err != nil {
		panic(err)
	}
	tripID := trip.TripID
	lat := trip.Latitude
	lng := trip.Longitude
	time := trip.Datetime
	vendorID := trip.VendorID
	status := trip.Status
	if status == "start" {
		_, err = db.Exec("INSERT INTO trips(tripID,vendorID,startTime,startLat,startLng,endTime,endLat,endLng,status) VALUES($1,$2,$3,$4,$5,NULL,NULL,NULL,$6);", tripID, vendorID, time, lat, lng, status)
		if err != nil {
			panic(err)
		}
	} else {
		_, err = db.Exec("UPDATE trips SET endTime = $1, endLat = $2, endLng = $3, status = $4 WHERE tripID = $5", time, lat, lng, status, tripID)
		if err != nil {
			panic(err)
		}
	}

}
