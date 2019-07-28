package main

import (
	"encoding/gob"
	"fmt"
	"log"
	"os"
)

type commandDB struct {
	path  string
	dbMap map[string]irCode
}

func CreateDB(path string) (*commandDB, error) {
	db := &commandDB{
		path:  path,
		dbMap: make(map[string]irCode),
	}

	file, err := os.Open(path)
	if err == nil {
		defer file.Close()

		e := gob.NewDecoder(file)
		err = e.Decode(&db.dbMap)
	}

	if err != nil {
		// create file if decode fails
		log.Printf("err:%v\n", err)
		file, err = os.Create(path)
		file.Close()
		if err != nil {
			return nil, err
		}
	}

	return db, nil
}

func (db *commandDB) get(name string) (irCode, error) {
	ir, ok := db.dbMap[name]
	if !ok {
		return nil, fmt.Errorf("%v not found on db", name)
	}
	return ir, nil
}

func (db *commandDB) set(name string, ircode irCode) error {
	db.dbMap[name] = ircode

	f, err := os.Create(db.path)
	if err != nil {
		return fmt.Errorf("file create fail: %v", db.path)
	}
	defer f.Close()
	e := gob.NewEncoder(f)
	return e.Encode(db.dbMap)
}
