package main

import (
	"fmt"
	"net/http"
	"runtime"

	"github.com/labstack/echo/v4"
	"github.com/labstack/echo/v4/middleware"
)

// ServiceStatus
type ReqMemoryOperation struct {
	MBs uint64 `json:"mbs" form:"mbs" query:"mbs"` // how mbs to allocate
}

type ResMemoryOperation struct {
	Allocated      uint64 `json:"allocated" form:"allocated" query:"allocated"`                   // how many MBs allocated to allocate
	TotalAllocated uint64 `json:"total_allocated" form:"total_allocated" query:"total_allocated"` // how many MBs totally allocated
	Sys            uint64 `json:"sys" form:"sys" query:"sys"`                                     // how many MBs system uses
	NumGC          uint64 `json:"num_gc" form:"num_gc" query:"num_gc"`                            // how many times GC works
}

func bToMb(b uint64) uint64 {
	return b / 1024 / 1024
}

// https://golangcode.com/print-the-current-memory-usage/
func memoryUsage() *ResMemoryOperation {
	// For info on each, see: https://golang.org/pkg/runtime/#MemStats
	var m runtime.MemStats
	runtime.ReadMemStats(&m)
	res := &ResMemoryOperation{
		Allocated:      bToMb(m.Alloc),
		TotalAllocated: bToMb(m.TotalAlloc),
		Sys:            bToMb(m.Sys),
		NumGC:          uint64(m.NumGC),
	}
	fmt.Printf("Alloc = %v MiB", bToMb(m.Alloc))
	fmt.Printf("\tTotalAlloc = %v MiB", bToMb(m.TotalAlloc))
	fmt.Printf("\tSys = %v MiB", bToMb(m.Sys))
	fmt.Printf("\tNumGC = %v\n", m.NumGC)
	return res
}

var _memoryAllocated []byte = nil

// Handler
func allocMemory(c echo.Context) (err error) {
	mp := new(ReqMemoryOperation)
	if err = c.Bind(mp); err != nil {
		return err
	}
	println(1024 * 1024 * mp.MBs)
	_memoryAllocated = make([]byte, 1024*1024*mp.MBs)
	_memoryAllocated[0] = 0
	return c.JSON(http.StatusCreated, memoryUsage())
}

// Handler
func deallocMemory(c echo.Context) (err error) {
	_memoryAllocated = nil
	runtime.GC()
	return c.JSON(http.StatusCreated, memoryUsage())
}

func startService() {

	e := echo.New()

	// Middleware
	e.Use(middleware.Logger())
	e.Use(middleware.Recover())
	// Routes
	e.GET("/alloc_memory", allocMemory)
	e.GET("/dealloc_memory", deallocMemory)

	// Start server
	e.Logger.Info("Listening at 1323")
	e.Logger.Fatal(e.Start(":1323"))
}

func main() {
	startService()
}
