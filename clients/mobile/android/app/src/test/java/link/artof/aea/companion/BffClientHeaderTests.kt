package link.artof.aea.companion

import io.ktor.client.HttpClient
import io.ktor.client.engine.mock.MockEngine
import io.ktor.client.engine.mock.respond
import io.ktor.client.request.HttpRequestData
import io.ktor.http.HttpHeaders
import io.ktor.http.HttpStatusCode
import io.ktor.http.headersOf
import kotlinx.coroutines.runBlocking
import link.artof.aea.companion.data.api.BffClient
import org.junit.Assert.assertEquals
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
}
