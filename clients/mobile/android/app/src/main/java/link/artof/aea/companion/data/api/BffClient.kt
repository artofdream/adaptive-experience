package link.artof.aea.companion.data.api

import io.ktor.client.HttpClient
import io.ktor.client.engine.cio.CIO
import io.ktor.client.plugins.HttpTimeout
import io.ktor.client.plugins.contentnegotiation.ContentNegotiation
import io.ktor.client.request.header
import io.ktor.client.request.request
import io.ktor.client.request.setBody
import io.ktor.client.statement.HttpResponse
import io.ktor.client.statement.bodyAsText
import io.ktor.http.ContentType
import io.ktor.http.HttpHeaders
import io.ktor.http.HttpMethod
import io.ktor.http.contentType
import io.ktor.serialization.kotlinx.json.json
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.jsonObject
import kotlinx.serialization.json.jsonPrimitive
import link.artof.aea.companion.data.model.AcceptedResponse
import link.artof.aea.companion.data.model.BffException
import link.artof.aea.companion.data.model.CheckoutRequest
import link.artof.aea.companion.data.model.ConversationMessageRequest
import link.artof.aea.companion.data.model.ConversationResponse
import link.artof.aea.companion.data.model.DeliveryRequest
import link.artof.aea.companion.data.model.SelectionRequest
import link.artof.aea.companion.data.model.SessionCreateResponse
import link.artof.aea.companion.data.model.SharedUnderstandingResponse
import link.artof.aea.companion.data.model.WorkspaceResponse
import java.util.concurrent.atomic.AtomicReference

/**
 * Live Edge BFF client for https://aea.artof.link.
 *
 * Auth contract (matches edge/bff/aea_bff/app.py + web app.js):
 * - Subject gate: public browser Bearer (`local-browser-token`), same as web — not a secret.
 * - Session identity: cookie jar (`__Host-aea_session` + `__Host-aea_recall`) from POST /session.
 * - Mutating POSTs: `X-CSRF-Token` from session create body.
 * - Do NOT send the session id as Authorization Bearer.
 */
open class BffClient(
    private val baseUrl: String = DEFAULT_BASE_URL,
    private val clientBearerToken: String = PUBLIC_BROWSER_BEARER,
    private val httpClient: HttpClient? = null
) {
    private val json = Json {
        ignoreUnknownKeys = true
        isLenient = true
        // Keep observed_context_version=0 and empty options in request bodies.
        encodeDefaults = true
        explicitNulls = false
    }

    private val csrfToken = AtomicReference("")
    private val cookieJar = java.util.concurrent.ConcurrentHashMap<String, String>()

    // Lazy so FakeBffClient unit doubles never open a socket.
    private val client: HttpClient by lazy {
        httpClient ?: HttpClient(CIO) {
            expectSuccess = false
            install(HttpTimeout) {
                requestTimeoutMillis = 30_000
                connectTimeoutMillis = 15_000
                socketTimeoutMillis = 30_000
            }
            install(ContentNegotiation) {
                json(json)
            }
        }
    }

    open suspend fun createSession(): SessionCreateResponse {
        val response = rawRequest(HttpMethod.Post, "/api/v1/session")
        val payload = decodeOrThrow<SessionCreateResponse>(response, expected = setOf(201))
        csrfToken.set(payload.csrfToken)
        return payload
    }

    open suspend fun postConversationMessage(
        messageText: String,
        observedContextVersion: Int
    ): AcceptedResponse {
        val response = rawRequest(
            HttpMethod.Post,
            "/api/v1/conversation/messages",
            body = ConversationMessageRequest(messageText, observedContextVersion),
            csrf = true
        )
        return decodeOrThrow(response, expected = setOf(202))
    }

    open suspend fun getSharedUnderstanding(): SharedUnderstandingResponse {
        val response = rawRequest(HttpMethod.Get, "/api/v1/shared-understanding")
        return decodeOrThrow(response, expected = setOf(200))
    }

    open suspend fun getConversation(): ConversationResponse {
        val response = rawRequest(HttpMethod.Get, "/api/v1/conversation")
        return decodeOrThrow(response, expected = setOf(200))
    }

    open suspend fun getWorkspace(): WorkspaceResponse {
        val response = rawRequest(HttpMethod.Get, "/api/v1/workspace")
        return decodeOrThrow(response, expected = setOf(200))
    }

    open suspend fun postSelection(request: SelectionRequest): AcceptedResponse {
        val response = rawRequest(HttpMethod.Post, "/api/v1/selection", body = request, csrf = true)
        return decodeOrThrow(response, expected = setOf(202))
    }

    open suspend fun postDelivery(request: DeliveryRequest): AcceptedResponse {
        val response = rawRequest(HttpMethod.Post, "/api/v1/delivery", body = request, csrf = true)
        return decodeOrThrow(response, expected = setOf(202))
    }

    open suspend fun postOrder(): AcceptedResponse {
        val response = rawRequest(HttpMethod.Post, "/api/v1/order", body = emptyMap<String, String>(), csrf = true)
        return decodeOrThrow(response, expected = setOf(202))
    }

    open suspend fun postCheckout(request: CheckoutRequest): AcceptedResponse {
        val response = rawRequest(HttpMethod.Post, "/api/v1/checkout", body = request, csrf = true)
        return decodeOrThrow(response, expected = setOf(202))
    }

    fun currentCsrfToken(): String = csrfToken.get()

    open fun close() {
        if (httpClient == null) {
            client.close()
        }
    }

    private suspend fun rawRequest(
        method: HttpMethod,
        path: String,
        body: Any? = null,
        csrf: Boolean = false
    ): HttpResponse {
        // Manual cookie jar: ktor-client-cookies is not published for 3.0.1 on Maven
        // Central; CIO + core still suffice if we mirror Set-Cookie / Cookie.
        val response = client.request("$baseUrl$path") {
            this.method = method
            header(HttpHeaders.Authorization, "Bearer $clientBearerToken")
            if (cookieJar.isNotEmpty()) {
                header(
                    HttpHeaders.Cookie,
                    cookieJar.entries.joinToString("; ") { "${it.key}=${it.value}" }
                )
            }
            if (csrf) {
                val token = csrfToken.get()
                if (token.isNotBlank()) {
                    header("X-CSRF-Token", token)
                }
            }
            if (body != null && method != HttpMethod.Get) {
                contentType(ContentType.Application.Json)
                setBody(body)
            }
        }
        // Parse Set-Cookie headers (name=value; attrs...)
        response.headers.getAll(HttpHeaders.SetCookie).orEmpty().forEach { raw ->
            val pair = raw.substringBefore(';').trim()
            val eq = pair.indexOf('=')
            if (eq > 0) {
                val name = pair.substring(0, eq).trim()
                val value = pair.substring(eq + 1).trim()
                if (name.isNotEmpty()) {
                    cookieJar[name] = value
                }
            }
        }
        return response
    }

    private suspend inline fun <reified T> decodeOrThrow(
        response: HttpResponse,
        expected: Set<Int>
    ): T {
        val status = response.status.value
        val text = response.bodyAsText()
        if (status !in expected) {
            val code = parseErrorCode(text) ?: "http_$status"
            throw BffException(
                statusCode = status,
                errorCode = code,
                message = "BFF $status $code"
            )
        }
        if (text.isBlank()) {
            throw BffException(status, "empty_body", "BFF returned empty body")
        }
        return json.decodeFromString(text)
    }

    private fun parseErrorCode(body: String): String? {
        return try {
            val root = json.parseToJsonElement(body).jsonObject
            root["error"]?.jsonPrimitive?.content
                ?: root["code"]?.jsonPrimitive?.content
        } catch (_: Exception) {
            null
        }
    }

    companion object {
        const val DEFAULT_BASE_URL = "https://aea.artof.link"
        /** Public client token embedded in web `app.js` (not a secret / not session auth). */
        const val PUBLIC_BROWSER_BEARER = "local-browser-token"
        /** ADR-013 opaque vault reference mirrored from web SESSION_PAYMENT_REFERENCE. */
        const val SESSION_PAYMENT_REFERENCE = "session_pay_ref"
        /** ADR-013 opaque destination mirrored from web SESSION_DESTINATION_REFERENCE. */
        const val SESSION_DESTINATION_REFERENCE = "home"
    }
}
