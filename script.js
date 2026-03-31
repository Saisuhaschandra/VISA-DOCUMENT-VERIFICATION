// ---------- BASIC SETUP ----------
const TOTAL_DOCS = 17;

// store uploaded documents
const uploadedDocs = new Set();


// ---------- UPDATE PROGRESS ----------
function updateProgress() {
    const count = uploadedDocs.size;
    const percent = Math.round((count / TOTAL_DOCS) * 100);

    document.getElementById("progressPercent").innerText = percent + "%";
    document.getElementById("progressText").innerText =
        `${count} of ${TOTAL_DOCS} documents uploaded`;
}


// ---------- HANDLE FILE SELECTION ----------
document.querySelectorAll("input[type='file']").forEach(input => {

    input.addEventListener("change", function () {

        const docType = this.id;
        const status = document.getElementById(docType + "_status");

        // if user cancels selection
        if (!this.files || this.files.length === 0) {
            status.innerHTML = "";
            status.style.color = "";
            return;
        }

        // new file selected → reset old status
        status.innerHTML = "⚠️";
        status.style.color = "orange";
    });

});


// ---------- UPLOAD DOCUMENT ----------
function uploadDoc(docType) {

    const input = document.getElementById(docType);
    const status = document.getElementById(docType + "_status");

    // no file selected
    if (!input.files || input.files.length === 0) {
        status.innerHTML = "";
        return;
    }

    const file = input.files[0];

    // show loading
    status.innerHTML = "Uploading...";
    status.style.color = "orange";

    const formData = new FormData();
    formData.append("document", file);
    formData.append("type", docType);

    fetch("/upload", {
        method: "POST",
        body: formData
    })
    .then(res => res.json())
    .then(data => {

        // ✅ Ignore validation → always show uploaded
        status.innerHTML = "✔ Uploaded";
        status.style.color = "green";

        uploadedDocs.add(docType);
        updateProgress();

    })
    .catch(() => {
        status.innerHTML = "✖ Upload failed";
        status.style.color = "red";
    });
}


// ---------- VERIFY DOCUMENTS ----------
function verifyDocs() {

    const resultBox = document.getElementById("finalResult");

    // allow verify only if at least 1 doc uploaded
    if (uploadedDocs.size === 0) {
        resultBox.innerHTML = "❌ Please upload at least one document";
        resultBox.style.color = "red";
        return;
    }

    resultBox.innerHTML = "Verifying...";
    resultBox.style.color = "orange";

    fetch("/verify")
        .then(res => res.json())
        .then(data => {

            const isSuccess = data.status === "success" && data.result.includes("✅");

            resultBox.innerHTML = data.result || "Verification failed";
            resultBox.style.color = isSuccess ? "green" : "red";

        })
        .catch(() => {
            resultBox.innerHTML = "Server error";
            resultBox.style.color = "red";
        });
}