/*
this test fails because
the facet active javascript
file is not loaded correctly
with selected orgranization page.
TODO: further investigate why
the module is not correctly
imported
*/


describe("searching datasets by organizations", ()=>{

    beforeEach(()=>{
        cy.visit("/dataset/")
    })

    it("search datasets by organization", ()=>{
        cy.get("a").contains("Organisations").click()
        .get("a[href='/organization/csi']").click()
        .get(".dataset-item").its("length").should("gt",0)
    })


})
