package com.choptyuk.service;

import com.choptyuk.model.*;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.io.*;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.Instant;
import java.time.format.DateTimeFormatter;
import java.util.*;

/**
 * Multi-format report generation service.
 *
 * Supported formats: JSON, HTML, CSV, TXT, MD, DOCX (Apache POI), PDF (iText).
 * Reports are structured with results first, then execution logs.
 */
@Service
@Slf4j
public class ReportService {

    private final ObjectMapper objectMapper;
    private final VerificationService verificationService;
    private final SimulationService simulationService;
    private final String reportDir;

    public ReportService(VerificationService verificationService, SimulationService simulationService) {
        this.verificationService = verificationService;
        this.simulationService = simulationService;
        this.objectMapper = new ObjectMapper();
        this.objectMapper.enable(SerializationFeature.INDENT_OUTPUT);
        this.objectMapper.disable(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS);
        this.reportDir = System.getProperty("choptyuk.reports.dir", "reports");
    }

    /**
     * Report metadata for listing.
     */
    public record ReportInfo(
            String filename,
            String format,
            long sizeBytes,
            Instant createdAt,
            String description
    ) {}

    /**
     * Generates a report in the specified format.
     */
    public byte[] generateReport(String format) throws IOException {
        log.info("Generating report in format: {}", format);

        VerificationService.VerificationResult verification = verificationService.verifyAll();

        return switch (format.toUpperCase()) {
            case "JSON" -> generateJson(verification);
            case "HTML" -> generateHtml(verification);
            case "CSV" -> generateCsv(verification);
            case "TXT" -> generateTxt(verification);
            case "MD" -> generateMarkdown(verification);
            case "DOCX" -> generateDocx(verification);
            case "PDF" -> generatePdf(verification);
            default -> throw new IllegalArgumentException("Unsupported format: " + format);
        };
    }

    /**
     * Lists all available report files.
     */
    public List<ReportInfo> listReports() {
        List<ReportInfo> reports = new ArrayList<>();
        Path dir = Paths.get(reportDir);

        if (Files.exists(dir)) {
            try {
                Files.list(dir).forEach(path -> {
                    if (Files.isRegularFile(path)) {
                        String name = path.getFileName().toString();
                        String ext = name.substring(name.lastIndexOf('.') + 1).toUpperCase();
                        try {
                            reports.add(new ReportInfo(name, ext, Files.size(path),
                                    Instant.from(DateTimeFormatter.ofPattern("yyyy-MM-dd_HH-mm-ss")
                                            .parse(name.replaceAll(".*_(\\d{4}-\\d{2}-\\d{2}_\\d{2}-\\d{2}-\\d{2}).*", "$1"))),
                                    "Choptyuk verification report"));
                        } catch (Exception e) {
                            reports.add(new ReportInfo(name, ext, 0, Instant.now(), "Report"));
                        }
                    }
                });
            } catch (IOException e) {
                log.warn("Could not list reports directory", e);
            }
        }

        return reports;
    }

    /**
     * Saves a report to disk and returns the file path.
     */
    public String saveReport(String format) throws IOException {
        byte[] content = generateReport(format);
        Path dir = Paths.get(reportDir);
        Files.createDirectories(dir);

        String timestamp = DateTimeFormatter.ofPattern("yyyy-MM-dd_HH-mm-ss").format(Instant.now());
        String filename = "choptyuk_report_" + timestamp + "." + format.toLowerCase();
        Path filePath = dir.resolve(filename);
        Files.write(filePath, content);

        log.info("Report saved: {}", filePath);
        return filePath.toString();
    }

    private byte[] generateJson(VerificationService.VerificationResult result) throws IOException {
        Map<String, Object> report = new LinkedHashMap<>();
        report.put("title", "Choptyuk Spinor Monograph Verification Report");
        report.put("timestamp", Instant.now().toString());

        // Results first
        Map<String, Object> results = new LinkedHashMap<>();
        results.put("allPassed", result.allPassed());
        results.put("totalChecks", result.totalChecks());
        results.put("passedChecks", result.passedChecks());
        results.put("failedChecks", result.failedChecks());
        results.put("deltaChBase", result.choptyukFormula().getDeltaChBase());
        results.put("deltaChHigher", result.choptyukFormula().getDeltaChHigher());
        results.put("deltaObserved", result.choptyukFormula().getDeltaObserved());
        results.put("deviationBase", result.choptyukFormula().getDeviationBase());
        results.put("deviationHigher", result.choptyukFormula().getDeviationHigher());
        results.put("relativeErrorBase", result.choptyukFormula().relativeErrorBase());
        results.put("relativeErrorHigher", result.choptyukFormula().relativeErrorHigher());
        report.put("results", results);

        // Checks
        report.put("checks", result.checks());

        // Klein curve
        report.put("kleinCurve", Map.of(
                "genus", result.kleinCurve().getGenus(),
                "pslOrder", result.kleinCurve().getPslOrder(),
                "lambda1", result.kleinCurve().getLambda1(),
                "scalarCurvature", result.kleinCurve().getScalarCurvature(),
                "area", result.kleinCurve().getArea()
        ));

        // Spinor phases
        report.put("spinorPhases", Map.of(
                "deltaA", result.spinorPhases().getDeltaA(),
                "deltaB", result.spinorPhases().getDeltaB(),
                "deltaC", result.spinorPhases().getDeltaC(),
                "numStructures", result.spinorPhases().getNumStructures()
        ));

        // QNM events
        List<Map<String, Object>> qnmList = new ArrayList<>();
        for (QNMEvent event : result.qnmEvents()) {
            Map<String, Object> qnm = new LinkedHashMap<>();
            qnm.put("eventName", event.getEventName());
            qnm.put("date", event.getDate());
            qnm.put("remnantMassSolar", event.getRemnantMassSolar());
            qnm.put("observedFreqHz", event.getObservedFreqHz());
            qnm.put("predictedFreqHz", event.getPredictedFreqHz());
            qnm.put("relativeError", event.getRelativeError());
            qnm.put("snr", event.getSnr());
            qnmList.add(qnm);
        }
        report.put("qnmEvents", qnmList);

        // Execution logs
        report.put("executionLogs", List.of(
                Map.of("time", Instant.now().toString(), "level", "INFO", "message", "Report generated successfully")
        ));

        return objectMapper.writeValueAsBytes(report);
    }

    private byte[] generateHtml(VerificationService.VerificationResult result) {
        StringBuilder sb = new StringBuilder();
        sb.append("<!DOCTYPE html><html><head><title>Choptyuk Verification Report</title>");
        sb.append("<style>body{font-family:sans-serif;max-width:900px;margin:0 auto;padding:20px}");
        sb.append("table{border-collapse:collapse;width:100%}th,td{border:1px solid #ddd;padding:8px;text-align:left}");
        sb.append("th{background:#333;color:#fff}.pass{color:#0a0}.fail{color:#a00}</style></head><body>");
        sb.append("<h1>Choptyuk Spinor Monograph Verification Report</h1>");
        sb.append("<p>Generated: ").append(Instant.now()).append("</p>");

        // Results summary
        sb.append("<h2>Results Summary</h2>");
        sb.append("<p>Status: <strong class=\"").append(result.allPassed() ? "pass" : "fail").append("\">");
        sb.append(result.allPassed() ? "ALL PASSED" : "FAILED").append("</strong></p>");
        sb.append("<p>Checks: ").append(result.passedChecks()).append("/").append(result.totalChecks()).append(" passed</p>");

        sb.append("<h3>Key Values</h3><table><tr><th>Value</th><th>Result</th></tr>");
        sb.append(tr("Delta_Ch (base)", fmt(result.choptyukFormula().getDeltaChBase())));
        sb.append(tr("Delta_Ch (higher)", fmt(result.choptyukFormula().getDeltaChHigher())));
        sb.append(tr("Delta_observed", fmt(result.choptyukFormula().getDeltaObserved())));
        sb.append(tr("Deviation (base)", fmt(result.choptyukFormula().getDeviationBase())));
        sb.append(tr("Relative error (base)", fmtPct(result.choptyukFormula().relativeErrorBase())));
        sb.append("</table>");

        // Checks table
        sb.append("<h2>Verification Checks</h2><table>");
        sb.append("<tr><th>Check</th><th>Expected</th><th>Actual</th><th>Status</th></tr>");
        for (VerificationService.VerificationCheck check : result.checks()) {
            sb.append("<tr><td>").append(check.name()).append("</td>");
            sb.append("<td>").append(fmt(check.expected())).append("</td>");
            sb.append("<td>").append(fmt(check.actual())).append("</td>");
            sb.append("<td class=\"").append(check.passed() ? "pass" : "fail").append("\">");
            sb.append(check.passed() ? "PASS" : "FAIL").append("</td></tr>");
        }
        sb.append("</table>");

        // QNM events
        sb.append("<h2>LIGO QNM Predictions</h2><table>");
        sb.append("<tr><th>Event</th><th>Mass (M_sun)</th><th>f_obs (Hz)</th><th>f_pred (Hz)</th><th>Rel. Error</th><th>SNR</th></tr>");
        for (QNMEvent event : result.qnmEvents()) {
            sb.append("<tr><td>").append(event.getEventName()).append("</td>");
            sb.append("<td>").append(fmt(event.getRemnantMassSolar())).append("</td>");
            sb.append("<td>").append(fmt(event.getObservedFreqHz())).append("</td>");
            sb.append("<td>").append(fmt(event.getPredictedFreqHz())).append("</td>");
            sb.append("<td>").append(fmtPct(event.getRelativeError())).append("</td>");
            sb.append("<td>").append(fmt(event.getSnr())).append("</td></tr>");
        }
        sb.append("</table>");

        sb.append("<hr><p><em>Execution completed at ").append(Instant.now()).append("</em></p>");
        sb.append("</body></html>");
        return sb.toString().getBytes();
    }

    private byte[] generateCsv(VerificationService.VerificationResult result) {
        StringBuilder sb = new StringBuilder();
        sb.append("Check,Expected,Actual,Passed,Tolerance,Message\n");
        for (VerificationService.VerificationCheck check : result.checks()) {
            sb.append(String.format("\"%s\",%.8f,%.8f,%s,%.1e,\"%s\"\n",
                    check.name(), check.expected(), check.actual(),
                    check.passed(), check.tolerance(), check.message()));
        }
        sb.append("\n# QNM Events\n");
        sb.append("Event,Mass,f_obs,f_pred,RelError,SNR,Confidence\n");
        for (QNMEvent event : result.qnmEvents()) {
            sb.append(String.format("%s,%.1f,%.1f,%.1f,%.6f,%.1f,%.3f\n",
                    event.getEventName(), event.getRemnantMassSolar(),
                    event.getObservedFreqHz(), event.getPredictedFreqHz(),
                    event.getRelativeError(), event.getSnr(), event.getConfidence()));
        }
        return sb.toString().getBytes();
    }

    private byte[] generateTxt(VerificationService.VerificationResult result) {
        StringBuilder sb = new StringBuilder();
        sb.append("=" .repeat(70)).append("\n");
        sb.append("CHOPTYUK SPINOR MONOGRAPH VERIFICATION REPORT\n");
        sb.append("=".repeat(70)).append("\n");
        sb.append("Generated: ").append(Instant.now()).append("\n\n");

        sb.append("RESULTS SUMMARY\n").append("-".repeat(40)).append("\n");
        sb.append(String.format("  Status:     %s\n", result.allPassed() ? "ALL PASSED" : "FAILED"));
        sb.append(String.format("  Checks:     %d/%d passed\n", result.passedChecks(), result.totalChecks()));
        sb.append(String.format("  Delta_Ch:   %.6f\n", result.choptyukFormula().getDeltaChBase()));
        sb.append(String.format("  Delta_obs:  %.6f\n", result.choptyukFormula().getDeltaObserved()));
        sb.append(String.format("  Deviation:  %.6f\n", result.choptyukFormula().getDeviationBase()));
        sb.append(String.format("  Rel error:  %.6f%%\n\n", result.choptyukFormula().relativeErrorBase() * 100));

        sb.append("VERIFICATION CHECKS\n").append("-".repeat(40)).append("\n");
        for (VerificationService.VerificationCheck check : result.checks()) {
            sb.append(String.format("  [%s] %s: expected=%.6f, actual=%.6f\n",
                    check.passed() ? "PASS" : "FAIL", check.name(),
                    check.expected(), check.actual()));
        }

        sb.append("\nLIGO QNM PREDICTIONS\n").append("-".repeat(40)).append("\n");
        for (QNMEvent event : result.qnmEvents()) {
            sb.append(String.format("  %s: M=%.0f, f_obs=%.0f Hz, f_pred=%.0f Hz, err=%.2f%%\n",
                    event.getEventName(), event.getRemnantMassSolar(),
                    event.getObservedFreqHz(), event.getPredictedFreqHz(),
                    event.getRelativeError() * 100));
        }

        sb.append("\nEXECUTION LOG\n").append("-".repeat(40)).append("\n");
        sb.append("  Report generated successfully at ").append(Instant.now()).append("\n");
        return sb.toString().getBytes();
    }

    private byte[] generateMarkdown(VerificationService.VerificationResult result) {
        StringBuilder sb = new StringBuilder();
        sb.append("# Choptyuk Spinor Monograph Verification Report\n\n");
        sb.append("Generated: ").append(Instant.now()).append("\n\n");

        sb.append("## Results Summary\n\n");
        sb.append(String.format("| Metric | Value |\n|--------|-------|\n"));
        sb.append(String.format("| Status | %s |\n", result.allPassed() ? "✅ ALL PASSED" : "❌ FAILED"));
        sb.append(String.format("| Checks | %d/%d |\n", result.passedChecks(), result.totalChecks()));
        sb.append(String.format("| Delta_Ch (base) | %.6f |\n", result.choptyukFormula().getDeltaChBase()));
        sb.append(String.format("| Delta_Ch (higher) | %.6f |\n", result.choptyukFormula().getDeltaChHigher()));
        sb.append(String.format("| Delta_observed | %.6f |\n", result.choptyukFormula().getDeltaObserved()));
        sb.append(String.format("| Deviation (base) | %.6f |\n", result.choptyukFormula().getDeviationBase()));
        sb.append(String.format("| Relative error | %.4f%% |\n\n", result.choptyukFormula().relativeErrorBase() * 100));

        sb.append("## Verification Checks\n\n");
        sb.append("| Check | Expected | Actual | Status |\n|-------|----------|--------|--------|\n");
        for (VerificationService.VerificationCheck check : result.checks()) {
            sb.append(String.format("| %s | %.6f | %.6f | %s |\n",
                    check.name(), check.expected(), check.actual(),
                    check.passed() ? "✅" : "❌"));
        }

        sb.append("\n## LIGO QNM Predictions\n\n");
        sb.append("| Event | Mass (M☉) | f_obs (Hz) | f_pred (Hz) | Error | SNR |\n");
        sb.append("|-------|-----------|------------|-------------|-------|-----|\n");
        for (QNMEvent event : result.qnmEvents()) {
            sb.append(String.format("| %s | %.0f | %.0f | %.0f | %.2f%% | %.1f |\n",
                    event.getEventName(), event.getRemnantMassSolar(),
                    event.getObservedFreqHz(), event.getPredictedFreqHz(),
                    event.getRelativeError() * 100, event.getSnr()));
        }

        sb.append("\n---\n*Execution completed at ").append(Instant.now()).append("*\n");
        return sb.toString().getBytes();
    }

    private byte[] generateDocx(VerificationService.VerificationResult result) throws IOException {
        try (var out = new ByteArrayOutputStream()) {
            var doc = new org.apache.poi.xwpf.usermodel.XWPFDocument();

            var title = doc.createParagraph();
            title.setAlignment(org.apache.poi.xwpf.usermodel.ParagraphAlignment.CENTER);
            var titleRun = title.createRun();
            titleRun.setBold(true);
            titleRun.setFontSize(18);
            titleRun.setText("Choptyuk Spinor Monograph Verification Report");

            var date = doc.createParagraph();
            date.setAlignment(org.apache.poi.xwpf.usermodel.ParagraphAlignment.CENTER);
            date.createRun().setText("Generated: " + Instant.now());

            // Results section
            doc.createParagraph().createRun().setText("");
            var h2 = doc.createParagraph();
            h2.createRun().setBold(true);
            h2.createRun().setFontSize(14);
            h2.createRun().setText("Results Summary");

            addDocxLine(doc, "Status: " + (result.allPassed() ? "ALL PASSED" : "FAILED"));
            addDocxLine(doc, "Checks: " + result.passedChecks() + "/" + result.totalChecks() + " passed");
            addDocxLine(doc, String.format("Delta_Ch (base): %.6f", result.choptyukFormula().getDeltaChBase()));
            addDocxLine(doc, String.format("Delta_Ch (higher): %.6f", result.choptyukFormula().getDeltaChHigher()));
            addDocxLine(doc, String.format("Delta_observed: %.6f", result.choptyukFormula().getDeltaObserved()));
            addDocxLine(doc, String.format("Deviation: %.6f", result.choptyukFormula().getDeviationBase()));
            addDocxLine(doc, String.format("Relative error: %.4f%%", result.choptyukFormula().relativeErrorBase() * 100));

            // Checks table
            doc.createParagraph().createRun().setText("");
            var h2b = doc.createParagraph();
            h2b.createRun().setBold(true);
            h2b.createRun().setFontSize(14);
            h2b.createRun().setText("Verification Checks");

            var table = doc.createTable();
            var headerRow = table.getRow(0);
            headerRow.getCell(0).setText("Check");
            headerRow.addNewTableCell().setText("Expected");
            headerRow.addNewTableCell().setText("Actual");
            headerRow.addNewTableCell().setText("Status");

            for (VerificationService.VerificationCheck check : result.checks()) {
                var row = table.createRow();
                row.getCell(0).setText(check.name());
                row.getCell(1).setText(String.format("%.6f", check.expected()));
                row.getCell(2).setText(String.format("%.6f", check.actual()));
                row.getCell(3).setText(check.passed() ? "PASS" : "FAIL");
            }

            // Execution log
            doc.createParagraph().createRun().setText("");
            addDocxLine(doc, "Execution completed at " + Instant.now());

            doc.write(out);
            return out.toByteArray();
        }
    }

    private void addDocxLine(org.apache.poi.xwpf.usermodel.XWPFDocument doc, String text) {
        doc.createParagraph().createRun().setText(text);
    }

    private byte[] generatePdf(VerificationService.VerificationResult result) throws Exception {
        try (var out = new ByteArrayOutputStream()) {
            var document = new com.itextpdf.text.Document();
            com.itextpdf.text.pdf.PdfWriter.getInstance(document, out);
            document.open();

            var font = new com.itextpdf.text.Font(com.itextpdf.text.Font.FontFamily.COURIER, 10);
            var boldFont = new com.itextpdf.text.Font(com.itextpdf.text.Font.FontFamily.HELVETICA, 16,
                    com.itextpdf.text.Font.BOLD);

            document.add(new com.itextpdf.text.Paragraph("Choptyuk Spinor Monograph Verification Report", boldFont));
            document.add(new com.itextpdf.text.Paragraph("Generated: " + Instant.now(), font));
            document.add(com.itextpdf.text.Chunk.NEWLINE);

            // Results
            document.add(new com.itextpdf.text.Paragraph("RESULTS SUMMARY", boldFont));
            document.add(new com.itextpdf.text.Paragraph(
                    String.format("Status: %s", result.allPassed() ? "ALL PASSED" : "FAILED"), font));
            document.add(new com.itextpdf.text.Paragraph(
                    String.format("Checks: %d/%d passed", result.passedChecks(), result.totalChecks()), font));
            document.add(new com.itextpdf.text.Paragraph(
                    String.format("Delta_Ch (base): %.6f", result.choptyukFormula().getDeltaChBase()), font));
            document.add(new com.itextpdf.text.Paragraph(
                    String.format("Delta_Ch (higher): %.6f", result.choptyukFormula().getDeltaChHigher()), font));
            document.add(new com.itextpdf.text.Paragraph(
                    String.format("Delta_observed: %.6f", result.choptyukFormula().getDeltaObserved()), font));
            document.add(new com.itextpdf.text.Paragraph(
                    String.format("Deviation: %.6f", result.choptyukFormula().getDeviationBase()), font));
            document.add(new com.itextpdf.text.Paragraph(
                    String.format("Relative error: %.4f%%", result.choptyukFormula().relativeErrorBase() * 100), font));
            document.add(com.itextpdf.text.Chunk.NEWLINE);

            // Checks
            document.add(new com.itextpdf.text.Paragraph("VERIFICATION CHECKS", boldFont));
            for (VerificationService.VerificationCheck check : result.checks()) {
                document.add(new com.itextpdf.text.Paragraph(
                        String.format("[%s] %s: expected=%.6f, actual=%.6f",
                                check.passed() ? "PASS" : "FAIL", check.name(),
                                check.expected(), check.actual()), font));
            }

            document.add(com.itextpdf.text.Chunk.NEWLINE);
            document.add(new com.itextpdf.text.Paragraph("Execution completed at " + Instant.now(), font));

            document.close();
            return out.toByteArray();
        }
    }

    private String tr(String label, String value) {
        return "<tr><td>" + label + "</td><td>" + value + "</td></tr>";
    }

    private String fmt(double val) {
        return String.format("%.6f", val);
    }

    private String fmtPct(double val) {
        return String.format("%.4f%%", val * 100);
    }
}
