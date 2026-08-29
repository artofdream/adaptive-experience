package link.artof.aea.companion.data.api

import io.ktor.client.HttpClient
import io.ktor.client.call.body
import io.ktor.client.engine.cio.CIO
import io.ktor.client.plugins.contentnegotiation.ContentNegotiation
import io.ktor.client.request.get
import io.ktor.client.request.header
import io.ktor.client.request.post
import io.ktor.client.request.setBody
import io.ktor.http.ContentType
import io.ktor.http.contentType
import io.ktor.serialization.kotlinx.json.json
import link.artof.aea.companion.data.model.*
import kotlinx.serialization.json.Json

class BffClient(
    private val baseUrl: String = "https://aea.artof.link"
) {
    private val client = HttpClient(CIO) {
        install(ContentNegotiation) {
            json(Json {
                ignoreUnknownKeys = true
                isLenient = true
                prettyPrint = true
            })
        }
    }

    suspend fun createSession(): SessionResponse {
        return client.post("$baseUrl/api/v1/session") {
            contentType(ContentType.Application.Json)
        }.body()
    }

    suspend fun sendMessage(sessionToken: String, text: String): SharedUnderstanding {
        return client.post("$baseUrl/api/v1/conversation/messages") {
            header("Authorization", "Bearer $sessionToken")
            contentType(ContentType.Application.Json)
            setBody(mapOf("content" to text))
        }.body()
    }

    suspend fun getSharedUnderstanding(sessionToken: String): SharedUnderstanding {
        return client.get("$baseUrl/api/v1/shared-understanding") {
            header("Authorization", "Bearer $sessionToken")
        }.body()
    }

    suspend fun selectArrangement(sessionToken: String, sku: String): SharedUnderstanding {
        return client.post("$baseUrl/api/v1/selection") {
            header("Authorization", "Bearer $sessionToken")
            contentType(ContentType.Application.Json)
            setBody(SelectionRequest(sku))
        }.body()
    }

    suspend fun setDelivery(sessionToken: String, request: DeliveryRequest): SharedUnderstanding {
        return client.post("$baseUrl/api/v1/delivery") {
            header("Authorization", "Bearer $sessionToken")
            contentType(ContentType.Application.Json)
            setBody(request)
        }.body()
    }

    suspend fun checkout(sessionToken: String): OrderResult {
        return client.post("$baseUrl/api/v1/checkout") {
            header("Authorization", "Bearer $sessionToken")
            contentType(ContentType.Application.Json)
            setBody(CheckoutRequest(sessionToken))
        }.body()
    }
}
