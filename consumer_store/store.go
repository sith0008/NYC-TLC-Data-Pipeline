package main

import (
	"bytes"
	"database/sql"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"

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
	Zone      string
}
type CompleteTrip struct {
	TripID    string
	StartTime string
	EndTime   string
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
	createTables()
	consume()
}
func createTables() {
	statement := `
		CREATE TABLE IF NOT EXISTS tripStart (tripID TEXT NOT NULL PRIMARY KEY,
							vendorID INTEGER,
							startTime TEXT,
							startLat NUMERIC,
							startLng NUMERIC,
							status TEXT,
							startZone TEXT
							);`
	_, err := db.Exec(statement)
	if err != nil {
		panic(err)
	}
	statement = `
	CREATE TABLE IF NOT EXISTS tripEnd (tripID TEXT NOT NULL PRIMARY KEY,
						vendorID INTEGER,
						endTime TEXT,
						endLat NUMERIC,
						endLng NUMERIC,
						status TEXT,
						endZone TEXT
						);`
	_, err = db.Exec(statement)
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
	zone := trip.Zone
	if status == "start" {
		_, err = db.Exec("INSERT INTO tripStart (tripID,vendorID,startTime,startLat,startLng,status,startZone) VALUES($1,$2,$3,$4,$5,$6,$7);", tripID, vendorID, time, lat, lng, status, zone)
		if err != nil {
			panic(err)
		}
	} else {
		_, err = db.Exec("INSERT INTO tripEnd (tripID,vendorID,endTime,endLat,endLng,status,endZone) VALUES($1,$2,$3,$4,$5,$6,$7);", tripID, vendorID, time, lat, lng, status, zone)
		if err != nil {
			panic(err)
		}
		statement := `SELECT startTime FROM tripStart WHERE tripID=$1;`
		row := db.QueryRow(statement, tripID)
		var startTime string
		err = row.Scan(&startTime)
		if err == sql.ErrNoRows {
			fmt.Println("trip not found")
		} else if err != nil {
			log.Fatal(err)
		} else {
			var completeTrip CompleteTrip
			completeTrip.TripID = tripID
			completeTrip.StartTime = startTime
			completeTrip.EndTime = time
			completeTrip.Status = "complete"
			completeTripBytes, err := json.Marshal(completeTrip)
			if err != nil {
				log.Fatal(err)
			}
			response, err := http.Post("http://localhost:8080/completeTrip", "application/json", bytes.NewBuffer(completeTripBytes))
			if err != nil {
				log.Fatal(err)
			}
			defer response.Body.Close()
			completeTripBytesRes, err := ioutil.ReadAll(response.Body)
			if err != nil {
				log.Fatal(err)
			}
			fmt.Println(string(completeTripBytesRes))
		}
	}

}
