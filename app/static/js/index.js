function resetForm() {
    $("input#word").val("");
    $(".add-form").remove();
}

function getDefaults() {
    if (null !== window.localStorage.getItem("language")) {
        return {
            language: window.localStorage.getItem("language"),
            deck: window.localStorage.getItem("deck")
        }
    }
    return false;
}

/**
 * Store and load desired target language and Anki deck settings in local storage.
 * @param {string} language - The target language.
 * @param {string} deck - The Anki deck (scraped from Anki on backend).
 */

function setDefaults(language, deck) {
    window.localStorage.setItem("language", language);
    window.localStorage.setItem("deck", deck);
}

function populateDefaults() {
    const defaults = getDefaults();
    if (defaults) {
        $("select#decks").val(defaults.deck);
        $("select#language").val(defaults.language);
    }
}

function search() {
    $(".add-form").remove();
    const word_query = $("input#word").val();
    const deck_name = $("select#decks").val();
    const language = $("select#language").val();
    setDefaults(language, deck_name);
    $(".search-spinner").removeClass("d-none");
    $.get("/search",
        {
            word_query: word_query,
            deck_name: deck_name,
            language: language
        },
        function (data) {
            $(".container").append(data);
            searchImages(word_query, language, true);
            searchSentences(word_query, language);
            $(".search-spinner").addClass("d-none");
        }
    );
}

/**
 * Search Google Images for query.
 * Query inherited by main word query, but can be overridden.
 * @param {?string} query - The Google Images search query.
 * @param {?string} language - Current language setting.
 */
function searchImages(query, language, loadFirstPage) {
    if (!query) {
        $(".image-search-label-spinner").removeClass("d-none");
        query = $("input#image_query").val();
    }

    if (!language) {
        language = $("select#language").val();
    }

    $(".gallery img").remove();
    $(".image-search-result-spinner").removeClass("d-none");

    $.get("/search-images",
        {
            word_query: query,
            language, language,
        },
        function (data) {
            $(".image-search-label-spinner").addClass("d-none");
            $(".image-search-result-spinner").addClass("d-none");

            data.forEach(function (link) {
                $("<img/>").attr("src", link).addClass("img-thumbnail").appendTo(".gallery");
            });

            waitForSelectedGallery();
        }
    );
}

function playSound(el) {
    const filename = $(el).data("audio");
    const audio = new Audio(filename);
    audio.play();
}

/**
 * Collect all relevant form data and send to backend to be added as an Anki note.
 */
function add() {
    $(".add-spinner").removeClass("d-none");
    const searchFormData = $(".search-form").serializeArray().reduce(function (obj, item) {
        obj[item.name] = item.value;
        return obj;
    }, {});

    const addFormData = $(".add-form").serializeArray().reduce(function (obj, item) {
        obj[item.name] = item.value;
        return obj;
    }, {});

    const formData = $.extend(searchFormData, addFormData);

    const selectedImages = $.map($(".img-selected"), function (el) {
        return $(el).attr("src");
    });

    formData["image_paths"] = JSON.stringify(selectedImages);
    formData["audio_filename"] = $(".btn-audio").data("audio");
    delete formData["image_query"];

    $.post("/add", formData, function (data) {
        $(".add-spinner").addClass("d-none");
        $(".add-form").remove();
        $("input#word").val("").focus();
        $(".alert-success").slideDown();
        setTimeout(function () {
            $(".alert-success").slideUp();
        }, 2000);
    });
}


function imgSearchWatch() {
    $("body").on("click", ".btn-image-search", function () {
        searchImages(null, null, true);
    });
}

/**
 * Search sentences for query.
 * Query inherited by main word query, but can be overridden.
 * @param {?string} query
 * @param {?string} language
 */
function searchSentences(query, language) {
    console.log("Searching for sentences...")
    if (!query) {
        query = $("input#sentence_query").val();
    }

    if (!language) {
        language = $("select#language").val();
    }

    $.get("/search-sentences",
        {
            word_query: query,
            language, language,
        }).done(function (data) {
            $("#sentence_examples").empty();
            for (var i = 0; i < data.length; i++) {
                var example = data[i];
                var option = $('<option></option>').attr("value", example).text(example);
                $("#sentence_examples").append(option);
            }
        });
}

function sentenceSearchWatch() {
    console.log('Registering sentence on-click handler');
    $("body").on("click", ".btn-sentence-search", function () {
        searchSentences(null, null);
    });

    $("body").on('change', '#sentence_examples', function () {
        $("#sentence").attr("value", this.value);
        $("#sentence_blanked").attr("value", this.value.replace($("input#sentence_query").val(), '__'));
    })
}

/**
 * Setup click listeners on images.
 * Swap images from the search pane to the selected pane and vice versa.
 */
function imgSelectWatch() {
    var selectedImages = [];
    $("body").on("click", ".gallery img", function () {
        $(this).addClass("img-selected");
        selectedImages.push(this.src);
        $(this).detach().appendTo(".gallery-selected");
    })
        .on("click", ".gallery-selected img", function () {
            $(this).removeClass("img-selected");
            selectedImages.pop(this.src);
            $(this).detach().insertBefore(".load-more");
        });
}

function enterWatch() {
    $("body").on("keypress", "input#word", function (e) {
        if (e.which === 13) {
            e.preventDefault();
            search();
        }
    })
        .on("keypress", "input#image_query", function (e) {
            if (e.which === 13) {
                e.preventDefault();
                searchImages(null, null, true);
            }
        });
}

function waitForSelectedGallery() {
    const sel = ".gallery-selected";
    let checkExist = setInterval(function () {
        if ($(sel).length) {
            clearInterval(checkExist);
            pasteWatch();
            dndWatch();
        }
    }, 100);
}

/**
 * Watch for images in clipboard to be pasted in the selected pane.
 */
function pasteWatch() {
    const sel = ".gallery-selected";
    $(sel).pastableNonInputable()
        .off("pasteImage").on("pasteImage", function (e, data) {
        $("<img />")
            .attr("src", data.dataURL)
            .addClass("img-thumbnail img-selected")
            .appendTo(sel);
    });
}

/**
 * Setup drag n' drop listener on selected image pane.
 * This pane handles dragging files, not images from <img> tags in-browser.
 * Set dragged-in image sources as base64-encoded data.
 */
function dndWatch() {
    const sel = ".gallery-selected";
    $(sel).off("dragover").on("dragover", function(e) {
        e.stopPropagation();
        e.preventDefault();
        e.originalEvent.dataTransfer.dropEffect = "copy";
        $(this).addClass("dnd-over");
    })
        .off("drop").on("drop", function(e) {
            e.stopPropagation();
            e.preventDefault();
            const files = e.originalEvent.dataTransfer.files; // Array of all files

            for (let i=0, file; file=files[i]; i++) {
                if (file.type.match(/image.*/)) {
                    const reader = new FileReader();

                    reader.onload = function(e2) {
                        // finished reading file data.
                        $("<img />")
                            .attr("src", e2.target.result)
                            .addClass("img-thumbnail img-selected")
                            .appendTo(sel);
                    };

                    reader.readAsDataURL(file); // start reading the file data.
                }
            }
        });
}

$(document).ready(function () {
    populateDefaults();
    imgSearchWatch();
    imgSelectWatch();
    sentenceSearchWatch();
    enterWatch();
});