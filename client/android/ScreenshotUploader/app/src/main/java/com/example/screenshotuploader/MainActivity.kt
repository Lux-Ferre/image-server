package com.example.screenshotuploader

import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.app.Activity
import android.util.Log
import okhttp3.*
import org.apache.commons.io.IOUtils
import org.json.JSONObject
import java.io.IOException
import java.io.InputStream
import java.text.SimpleDateFormat
import java.util.*

class MainActivity : Activity() {

    companion object {
        const val TAG = "MainActivity"
        const val UPLOAD_URL = "https://img.luxferre.dev/upload"
        const val API_KEY = "secret_key"
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val intent = intent
        if (Intent.ACTION_SEND == intent.action && intent.type != null && intent.type!!.startsWith("image/")) {
            handleSendImage(intent)
        } else {
            finish()
        }
    }

    private fun handleSendImage(intent: Intent) {
        val imageUri: Uri? = intent.getParcelableExtra(Intent.EXTRA_STREAM)
        if (imageUri != null) {
            uploadScreenshot(imageUri)
        } else {
            finish()
        }
    }

    private fun uploadScreenshot(imageUri: Uri) {
        try {
            val fileName = generateFileName()
            val inputStream: InputStream? = contentResolver.openInputStream(imageUri)
            val imageData = IOUtils.toByteArray(inputStream)

            val client = OkHttpClient()
            val requestBody = MultipartBody.Builder()
                .setType(MultipartBody.FORM)
                .addFormDataPart("file", fileName, RequestBody.create(null, imageData))
                .build()

            val request = Request.Builder()
                .url(UPLOAD_URL)
                .post(requestBody)
                .addHeader("X-API-KEY", API_KEY)
                .build()

            client.newCall(request).enqueue(object : Callback {
                override fun onFailure(call: Call, e: IOException) {
                    Log.e(TAG, "Upload failed: ${e.message}")
                    finish()
                }

                override fun onResponse(call: Call, response: Response) {
                    if (response.isSuccessful) {
                        val responseBody = response.body?.string()
                        val jsonObject = JSONObject(responseBody)
                        val url = jsonObject.getString("url")
                        copyToClipboard(url)
                        Log.i(TAG, "Upload successful: $url")
                    } else {
                        Log.e(TAG, "Upload failed: ${response.message}")
                    }
                    finish()
                }
            })
        } catch (e: IOException) {
            Log.e(TAG, "Error uploading screenshot: ${e.message}")
            finish()
        }
    }

    private fun generateFileName(): String {
        val timeStamp = SimpleDateFormat("yyyy-MM-ddHHmmss", Locale.getDefault()).format(Date())
        return "android_screenshot_$timeStamp.png"
    }

    private fun copyToClipboard(text: String) {
        val clipboard = getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
        val clip = ClipData.newPlainText("uploaded_url", text)
        clipboard.setPrimaryClip(clip)
    }
}
