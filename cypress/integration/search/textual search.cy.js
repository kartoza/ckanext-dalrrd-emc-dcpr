describe("search for datasets via title", ()=>{
    beforeEach(()=>{
        cy.visit("/")
    })
    it("finds a dataset from the home page by text",()=>{
        cy.get("[data-testid='home_dataset_search_input']")
        .type("test dataset no.1")
        .get("[data-testid='home_search_submit']").click()
        .url().should("include","/dataset/?q=test+dataset+no.1")
        .get("[data-testid='search_item_anchor']").next().eq(0).
        should("have.text","dataset no 1")
    })

    it("finds a dataset from the home page by abstract",()=>{
        cy.get("[data-testid='home_dataset_search_input']")
        .type("Default abstract for test")
        .get("[data-testid='home_search_submit']").click()
        //.url().should("include","/dataset/?q=test+dataset+no.2")
        .get("[data-testid='search_item_anchor']").next().eq(0).
        should("have.text","dataset no 1_v.4")
    })

    it("finds a dataset from the home page by doi",()=>{
        cy.get("[data-testid='home_dataset_search_input']")
        .type("10.15493/SARVA.CSAG.10000280")
        .get("[data-testid='home_search_submit']").click()
        //.url().should("include","/dataset/?q=test+dataset+no.2")
        .get("[data-testid='search_item_anchor']").next().eq(0).
        should("have.text","dataset no 1_v.4")
    })

})


describe("search dataset by temporal range", ()=>{
    beforeEach(()=>{
        cy.visit("/dataset/")
    })
    it("finds datasets by start data",()=>{
        cy.get("[data-testid='temporal_search-start']")
        .type("2022-10-24{enter}")
    })

    it("finds datasets by end date", ()=>{
        cy.get("[data-testid='temporal_search-end']")
        .type("2022-10-25{enter}")

    })

    it("finds datasets temporal range (start-end)", ()=>{
        cy.get("[data-testid='temporal_search-start']")
        .type("2022-10-24{enter}")
        .get*("[data-testid='temporal_search-end']")
        .type("2022-10-24{enter}")


    })

})
