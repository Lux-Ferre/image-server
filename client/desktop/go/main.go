package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"github.com/gen2brain/beeep"
	"golang.design/x/clipboard"
	"io"
	"mime/multipart"
	"net/http"
	"os"
	"path/filepath"
)

type ApiResponse struct {
	UUID string `json:"uuid"`
	URL  string `json:"url"`
}

func main() {
	args := os.Args
	normalizedPath := ""

	if len(args) > 1 {
		inputPath := args[1]
		normalizedPath = filepath.FromSlash(inputPath)
	} else {
		createNotification("Error opening file", "No arguments passed")
	}

	url := "https://img.luxferre.dev/upload"
	apiKey := "secret_key"

	// Open the file
	file, openErr := os.Open(normalizedPath)
	if openErr != nil {
		createNotification("Error opening file", openErr.Error())
		return
	}
	defer func(file *os.File) {
		closeErr := file.Close()
		if closeErr != nil {
			createNotification("Error closing file", closeErr.Error())
		}
	}(file)

	// Create a buffer to store the form data
	body := &bytes.Buffer{}
	writer := multipart.NewWriter(body)

	// Create a form file field 'file' in the form-data
	part, formErr := writer.CreateFormFile("file", filepath.Base(file.Name()))
	if formErr != nil {
		createNotification("Error creating form file", formErr.Error())
		return
	}

	// Copy the file content into the form file
	_, copyErr := io.Copy(part, file)
	if copyErr != nil {
		createNotification("Error copying file", copyErr.Error())
		return
	}

	// Close the multipart writer to finalize the form data
	writeErr := writer.Close()
	if writeErr != nil {
		createNotification("Error closing writer", writeErr.Error())
		return
	}

	// Create a new POST request
	req, reqCreateErr := http.NewRequest("POST", url, body)
	if reqCreateErr != nil {
		createNotification("Error creating request", reqCreateErr.Error())
		return
	}

	// Set headers
	req.Header.Set("Content-Type", writer.FormDataContentType()) // multipart form-data header
	req.Header.Set("X-API-KEY", apiKey)

	// Create a client and send the request
	client := &http.Client{}
	resp, reqSendErr := client.Do(req)
	if reqSendErr != nil {
		createNotification("Error sending request", reqSendErr.Error())
		return
	}
	defer func(Body io.ReadCloser) {
		bodyCloseErr := Body.Close()
		if bodyCloseErr != nil {
			createNotification("Error closing body", bodyCloseErr.Error())
		}
	}(resp.Body)

	if resp.StatusCode != 201 {
		createNotification("Error uploading file", resp.Status)
		return
	}

	jsonBody, bodyReadErr := io.ReadAll(resp.Body)
	if bodyReadErr != nil {
		createNotification("Error reading body", bodyReadErr.Error())
	}
	var apiResponse ApiResponse
	if jsonParseErr := json.Unmarshal(jsonBody, &apiResponse); jsonParseErr != nil {
		createNotification("Error parsing JSON", jsonParseErr.Error())
		return
	}

	clipboardErr := clipboard.Init()
	if clipboardErr != nil {
		createNotification("Error initialising clipboard", clipboardErr.Error())
		return
	}

	clipboard.Write(clipboard.FmtText, []byte(apiResponse.URL))

	createNotification("Uploaded screenshot", apiResponse.URL)
}

func createNotification(title string, message string) {
	err := beeep.Notify(title, message, "")
	if err != nil {
		fmt.Println("Error creating notification: ", err)
	}
}
