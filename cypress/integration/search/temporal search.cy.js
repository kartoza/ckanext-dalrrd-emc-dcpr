describe("search dataset by temporal range", ()=>{
    //TODO: add a dataset that has these values
    beforeEach(()=>{
        cy.visit("/dataset/")
    })
    it("finds datasets by start data",()=>{
        cy.get("[data-testid='temporal_search-start']")
        .type("2022-10-24").trigger("change")
        .url().should("include","dataset/?ext_start_reference_date=2022-10-24")
    })

    it("finds datasets by end date", ()=>{
        cy.get("[data-testid='temporal_search-end']")
        .type("2022-10-25").trigger("change")
        .url().should("include","dataset/?ext_end_reference_date=2022-10-25")
    })

    it("finds datasets temporal range (start-end)", ()=>{
        cy.get("[data-testid='temporal_search-start']")
        .type("2022-10-24").trigger("change")
        .get("[data-testid='temporal_search-end']")
        .type("2022-10-25").trigger("change")
        .url().should("include","dataset/?ext_start_reference_date=2022-10-24&ext_end_reference_date=2022-10-25")

    })

})
