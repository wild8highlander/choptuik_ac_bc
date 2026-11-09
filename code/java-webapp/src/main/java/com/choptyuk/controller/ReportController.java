package com.choptyuk.controller;

import com.choptyuk.service.ReportService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * REST API controller for report generation and download.
 *
 * Endpoints:
 *   GET /api/reports/{format}  - Generate and download a report in the specified format
 *   GET /api/reports/list      - List all available report files
 *
 * Supported formats: JSON, HTML, CSV, TXT, MD, DOCX, PDF
 */
@RestController
@RequestMapping("/api/reports")
@Slf4j
public class ReportController {

    private final ReportService reportService;

    public ReportController(ReportService reportService) {
        this.reportService = reportService;
    }

    /**
     * Generate a report in the specified format and return it as a downloadable file.
     *
     * @param format the report format (json, html, csv, txt, md, docx, pdf)
     */
    @GetMapping("/{format}")
    public ResponseEntity<byte[]> getReport(@PathVariable String format) {
        log.info("GET /api/reports/{}", format);

        try {
            byte[] content = reportService.generateReport(format);

            MediaType mediaType = getMediaType(format);
            String filename = "choptyuk_report." + format.toLowerCase();

            return ResponseEntity.ok()
                    .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"" + filename + "\"")
                    .contentType(mediaType)
                    .contentLength(content.length)
                    .body(content);

        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().build();
        } catch (Exception e) {
            log.error("Error generating report", e);
            return ResponseEntity.internalServerError().build();
        }
    }

    /**
     * List all previously generated report files.
     */
    @GetMapping("/list")
    public ResponseEntity<List<ReportService.ReportInfo>> listReports() {
        log.info("GET /api/reports/list");
        return ResponseEntity.ok(reportService.listReports());
    }

    private MediaType getMediaType(String format) {
        return switch (format.toUpperCase()) {
            case "JSON" -> MediaType.APPLICATION_JSON;
            case "HTML" -> MediaType.TEXT_HTML;
            case "CSV" -> MediaType.parseMediaType("text/csv");
            case "TXT" -> MediaType.TEXT_PLAIN;
            case "MD" -> MediaType.parseMediaType("text/markdown");
            case "DOCX" -> MediaType.parseMediaType("application/vnd.openxmlformats-officedocument.wordprocessingml.document");
            case "PDF" -> MediaType.APPLICATION_PDF;
            default -> MediaType.APPLICATION_OCTET_STREAM;
        };
    }
}
