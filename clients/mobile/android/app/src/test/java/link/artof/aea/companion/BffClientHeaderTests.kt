package link.artof.aea.companion

import io.ktor.client.HttpClient
import io.ktor.client.engine.mock.MockEngine
import io.ktor.client.engine.mock.respond
import io.ktor.client.plugins.contentnegotiation.ContentNegotiation
import io.ktor.client.request.HttpRequestData
import io.ktor.http.HttpHeaders
import io.ktor.http.HttpStatusCode
import io.ktor.http.headersOf
import io.ktor.serialization.kotlinx.json.json
import kotlinx.coroutines.runBlocking
import kotlinx.serialization.json.Json
import link.artof.aea.companion.data.api.BffClient
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

/**
 * #368 — companion BFF requests carry X-AEA-Client for Grafana/native vs web split.
 * Captured via Ktor MockEngine (no network).
 */
class BffClientHeaderTests {

    @Test
    fun createSessionSendsCompanionAndroidClientHeader() = runBlocking {
        val captured = mutableListOf<HttpRequestData>()
        val engine = MockEngine { request ->
            captured += request
            respond(
                content = """{"csrf_token":"test-csrf"}""",
                status = HttpStatusCode.Created,
                headers = headersOf(HttpHeaders.ContentType, "application/json")
            )
        }
        val http = HttpClient(engine)
        val client = BffClient(
            baseUrl = "https://aea.artof.link",
            httpClient = http
        )
        try {
            client.createSession()
        } finally {
            http.close()
        }

        assertEquals(1, captured.size)
        val headers = captured[0].headers
        assertEquals(
            BffClient.CLIENT_HEADER_VALUE,
            headers[BffClient.CLIENT_HEADER_NAME]
        )
        assertEquals("companion-android", headers["X-AEA-Client"])
        assertTrue(headers[HttpHeaders.Authorization]!!.startsWith("Bearer "))
    }

    @Test
    fun clientHeaderConstantsMatchIssueContract() {
        assertEquals("X-AEA-Client", BffClient.CLIENT_HEADER_NAME)
        assertEquals("companion-android", BffClient.CLIENT_HEADER_VALUE)
    }

    @Test
    fun postEscalationSendsReasonOnlyAndCompanionHeader() = runBlocking {
        val captured = mutableListOf<HttpRequestData>()
        val engine = MockEngine { request ->
            captured += request
            if (request.url.encodedPath.endsWith("/session")) {
                return@MockEngine respond(
                    content = """{"csrf_token":"test-csrf"}""",
                    status = HttpStatusCode.Created,
                    headers = headersOf(HttpHeaders.ContentType, "application/json")
                )
            }
            respond(
                content = """{"accepted":true,"code":"escalation_recorded","message_id":"esc-1","acknowledgement":"ok","escalation_reason":"unresolved_request"}""",
                status = HttpStatusCode.Accepted,
                headers = headersOf(HttpHeaders.ContentType, "application/json")
            )
        }
        val http = HttpClient(engine) {
            install(ContentNegotiation) {
                json(Json {
                    ignoreUnknownKeys = true
                    isLenient = true
                    encodeDefaults = true
                    explicitNulls = false
                })
            }
        }
        val client = BffClient(
            baseUrl = "https://aea.artof.link",
            httpClient = http
        )
        try {
            client.createSession()
            val result = client.postEscalation("unresolved_request")
            assertEquals("escalation_recorded", result.code)
            assertEquals("unresolved_request", result.escalationReason)
        } finally {
            http.close()
        }

        val escalation = captured.last()
        assertEquals("/api/v1/support/escalation", escalation.url.encodedPath)
        assertEquals("companion-android", escalation.headers["X-AEA-Client"])
        assertEquals("test-csrf", escalation.headers["X-CSRF-Token"])
        assertFalse(escalation.url.encodedPath.contains("operator"))
    }
}
